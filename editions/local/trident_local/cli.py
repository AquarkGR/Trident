"""Trident on one local Qwen model: refine -> plan -> build -> verify -> report.
The model is sized to your RAM; each stage spends reasoning and context as its budget."""
import argparse
import os
import pathlib
import re
import tomllib

import ollama

from . import prompts, tools
from .report import write_report

CFG = tomllib.loads((pathlib.Path(__file__).parent / "presets.toml").read_text())
CHOICE_LINE = "'TIER: standard' or 'TIER: deep' (deep only for complex, architectural or cross-cutting work)."


def detect_ram_gb() -> int:
    try:
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3)
    except (ValueError, OSError, AttributeError):
        return 16


def pick_preset(ram_gb: int) -> dict:
    fits = [int(k) for k in CFG["ram"] if int(k) <= ram_gb]
    if not fits:
        raise SystemExit(f"{ram_gb} GB is below the smallest preset ({min(map(int, CFG['ram']))} GB).")
    return CFG["ram"][str(max(fits))]


class Engine:
    def __init__(self, preset: dict, budget: float, max_ctx: int | None):
        self.model, self.max_ctx, self.budget = preset["model"], max_ctx or preset["max_ctx"], budget
        self.client = ollama.Client()

    def ensure_model(self):
        try:
            self.client.show(self.model)
        except ollama.ResponseError:
            print(f"Pulling {self.model} (one-time download)...")
            self.client.pull(self.model)

    def budget_for(self, name: str) -> dict:
        s = CFG["stage"][name]
        sampling = CFG["sampling"]["thinking" if s["think"] else "direct"]
        num_ctx = int(self.max_ctx * s["ctx"])
        return {"think": s["think"], "options": {**sampling, "num_ctx": num_ctx,
                                                 "num_predict": int(s["predict"] * self.budget)}}

    def run(self, name: str, instructions: str, prompt: str, tool_fns: list, turns: int = 30):
        b = self.budget_for(name)
        tools.MAX_CHARS = min(20_000, b["options"]["num_ctx"])  # keep tool output inside the context budget
        by_name = {f.__name__: f for f in tool_fns}
        messages = [{"role": "system", "content": instructions}, {"role": "user", "content": prompt}]
        used = 0
        for _ in range(turns):
            r = self.client.chat(self.model, messages, tools=tool_fns or None, **b)
            used += (r.prompt_eval_count or 0) + (r.eval_count or 0)
            messages.append(r.message)
            if not r.message.tool_calls:
                break
            for call in r.message.tool_calls:
                fn = by_name.get(call.function.name)
                try:
                    out = fn(**call.function.arguments) if fn else f"unknown tool {call.function.name}"
                except Exception as e:
                    out = f"error: {e}"
                messages.append({"role": "tool", "content": str(out), "tool_name": call.function.name})
        mode = "reasoning on" if b["think"] else "reasoning off"
        spend = f"{mode} · ctx {b['options']['num_ctx']:,} · cap {b['options']['num_predict']:,} · {used:,} tokens"
        return r.message.content or "", spend


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("request", nargs="?")
    p.add_argument("--ram", type=int, help="machine RAM in GB (auto-detected if omitted)")
    p.add_argument("--budget", type=float, default=1.0, help="multiply every stage's reasoning budget")
    p.add_argument("--ctx", type=int, help="override the preset's max context")
    p.add_argument("--tier", choices=["standard", "deep"], help="override the planner's choice")
    p.add_argument("--cwd", default=".")
    p.add_argument("--yes", action="store_true", help="skip approvals (plan and shell commands)")
    p.add_argument("--dry-run", action="store_true", help="print the preset and stage budgets and exit")
    a = p.parse_args()

    ram = a.ram or detect_ram_gb()
    eng = Engine(pick_preset(ram), a.budget, a.ctx)
    if a.dry_run or not a.request:
        print(f"RAM {ram} GB -> {eng.model}, max context {eng.max_ctx:,}")
        for name in CFG["stage"]:
            b = eng.budget_for(name)
            print(f"  {name:15} think={str(b['think']):5} ctx={b['options']['num_ctx']:>7,} "
                  f"predict={b['options']['num_predict']:>6,}")
        return

    eng.ensure_model()
    tools.configure(a.cwd, a.yes)
    spend = {}
    spec, spend["Refine"] = eng.run("refine", prompts.REFINE, a.request, tools.READ_TOOLS[:2], turns=10)
    plan, spend["Plan"] = eng.run("plan", prompts.PLAN.replace("{choice_line}", CHOICE_LINE), spec, tools.READ_TOOLS)
    print(f"\n--- PLAN ---\n{plan}\n")
    if not a.yes and input("Proceed with build? [y/N] ").strip().lower() != "y":
        return

    m = re.search(r"TIER:\s*(standard|deep)", plan, re.I)
    tier = a.tier or (m.group(1).lower() if m else "standard")
    build_stage = f"build_{tier}"
    work = f"SPEC:\n{spec}\n\nPLAN:\n{plan}"

    build, spend["Build"] = eng.run(build_stage, prompts.BUILD, work, tools.BUILD_TOOLS, turns=60)
    verdict, spend["Verify"] = eng.run("verify", prompts.VERIFY, f"{work}\n\nBUILD:\n{build}", tools.CHECK_TOOLS)
    if "VERDICT: FAIL" in verdict:
        build, spend["Rebuild"] = eng.run(build_stage, prompts.BUILD, f"{work}\n\nFix:\n{verdict}", tools.BUILD_TOOLS, turns=60)
        verdict, spend["Re-verify"] = eng.run("verify", prompts.VERIFY, f"{work}\n\nBUILD:\n{build}", tools.CHECK_TOOLS)

    summary, spend["Summary"] = eng.run("summary", prompts.SUMMARY, f"{a.request}\n\n{build}\n\n{verdict}", [], turns=1)
    path = write_report(a.cwd, a.request, summary, f"{eng.model} · {ram} GB · {tier}", spend, plan, build, verdict)
    print(f"\n{summary}\nReport: {path}")


if __name__ == "__main__":
    main()
