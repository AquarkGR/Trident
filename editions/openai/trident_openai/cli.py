"""Trident on the OpenAI Agents SDK: refine -> plan (web research) -> build -> verify -> report."""
import argparse
import os
import pathlib
import re
import tomllib

from agents import Agent, ModelSettings, Runner, WebSearchTool, function_tool
from openai.types.shared import Reasoning

from . import prompts, tools
from .report import write_report

MODELS = tomllib.loads((pathlib.Path(__file__).parent / "models.toml").read_text())
CHOICE_LINE = "'TIER: standard' or 'TIER: deep' (deep only for complex, architectural or cross-cutting work)."


def stage(name: str) -> tuple[str, str]:
    cfg = MODELS[name]
    return os.getenv(f"TRIDENT_{name.upper()}_MODEL", cfg["model"]), cfg["effort"]


def run(name: str, instructions: str, prompt: str, tool_fns: list, extra_tools=(), turns: int = 30):
    model, effort = stage(name)
    agent = Agent(
        name=name, instructions=instructions, model=model,
        model_settings=ModelSettings(reasoning=Reasoning(effort=effort)),
        tools=[function_tool(f) for f in tool_fns] + list(extra_tools),
    )
    result = Runner.run_sync(agent, prompt, max_turns=turns)
    usage = result.context_wrapper.usage
    return str(result.final_output), f"{model} ({effort}) · {usage.total_tokens:,} tokens"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("request")
    p.add_argument("--cwd", default=".")
    p.add_argument("--tier", choices=["standard", "deep"], help="override the planner's choice")
    p.add_argument("--yes", action="store_true", help="skip approvals (plan and shell commands)")
    p.add_argument("--dry-run", action="store_true", help="print the stage configuration and exit")
    a = p.parse_args()

    if a.dry_run:
        for name in MODELS:
            print(f"{name:15} {stage(name)[0]:20} effort={stage(name)[1]}")
        return

    tools.configure(a.cwd, a.yes)
    spend = {}
    spec, spend["Refine"] = run("refine", prompts.REFINE, a.request, tools.READ_TOOLS[:2], turns=10)
    plan, spend["Plan"] = run("plan", prompts.PLAN.replace("{choice_line}", CHOICE_LINE), spec,
                              tools.READ_TOOLS, [WebSearchTool()])
    print(f"\n--- PLAN ---\n{plan}\n")
    if not a.yes and input("Proceed with build? [y/N] ").strip().lower() != "y":
        return

    m = re.search(r"TIER:\s*(standard|deep)", plan, re.I)
    tier = a.tier or (m.group(1).lower() if m else "standard")
    build_stage = f"build_{tier}"
    work = f"SPEC:\n{spec}\n\nPLAN:\n{plan}"

    build, spend["Build"] = run(build_stage, prompts.BUILD, work, tools.BUILD_TOOLS, turns=60)
    verdict, spend["Verify"] = run("verify", prompts.VERIFY, f"{work}\n\nBUILD:\n{build}", tools.CHECK_TOOLS)
    if "VERDICT: FAIL" in verdict:
        build, spend["Rebuild"] = run(build_stage, prompts.BUILD, f"{work}\n\nFix:\n{verdict}", tools.BUILD_TOOLS, turns=60)
        verdict, spend["Re-verify"] = run("verify", prompts.VERIFY, f"{work}\n\nBUILD:\n{build}", tools.CHECK_TOOLS)

    summary, spend["Summary"] = run("refine", prompts.SUMMARY, f"{a.request}\n\n{build}\n\n{verdict}", [], turns=3)
    path = write_report(a.cwd, a.request, summary, f"OpenAI · {tier}", spend, plan, build, verdict)
    print(f"\n{summary}\nReport: {path}")


if __name__ == "__main__":
    main()
