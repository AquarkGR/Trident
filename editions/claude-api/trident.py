"""Trident without Claude Code: Haiku refines -> Fable plans -> Sonnet/Opus builds -> Haiku verifies -> report.

pip install anthropic claude-agent-sdk
export ANTHROPIC_API_KEY=...
python editions/claude-api/trident.py "build a CLI that converts CSV to parquet" --cwd ./myproject
"""
import argparse
import asyncio
import datetime
import pathlib
import re

import anthropic
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

MODELS = {
    "haiku": "claude-haiku-5-5",
    "fable": "claude-fable-5-1",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
}

LICENCES = (
    "Licence policy: allowed MIT, Apache-2.0, BSD-2/3-Clause, ISC, Unlicense, CC0, PSF, Zlib. "
    "Blocked GPL, AGPL, LGPL, SSPL, BUSL, non-commercial, source-available, or unknown."
)
REFINE_SYS = (
    "Rewrite the request as a task spec: Goal, Constraints, Inputs, Deliverables, "
    "Acceptance criteria (each testable). List open questions instead of guessing. Do not solve it."
)
PLAN_SYS = (
    "Reuse proven, permissively-licensed libraries and published methods instead of inventing. "
    f"{LICENCES} Output: 1) Sources (name, version, licence, URL), 2) numbered Plan, 3) Risks. "
    "Only cite sources you are confident exist. Last line exactly 'BUILDER: sonnet' or 'BUILDER: opus' "
    "(opus only for complex or architectural work)."
)
BUILD_SYS = (
    f"Implement the plan. Concise, readable code. {LICENCES} Pin versions. Before calling a library "
    "function, confirm it exists in the installed version; never guess a signature. Run code or tests "
    "and fix failures. Finish with: files changed, how to run, dependencies added (name, version, licence), open items."
)
VERIFY_SYS = (
    f"You did not write this code. Check, do not fix. {LICENCES} For each acceptance criterion give "
    "PASS/FAIL with evidence; check each added dependency's licence from installed metadata. "
    "Last line exactly 'VERDICT: PASS' or 'VERDICT: FAIL'."
)

client = anthropic.Anthropic()


def ask(model: str, system: str, prompt: str, max_tokens: int = 4000) -> str:
    resp = client.messages.create(
        model=MODELS[model], max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in resp.content if b.type == "text")


async def agent(model: str, system: str, prompt: str, cwd: str, tools: list[str]) -> str:
    options = ClaudeAgentOptions(
        model=MODELS[model], system_prompt=system, allowed_tools=tools,
        permission_mode="acceptEdits", cwd=cwd,
    )
    result = ""
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage):
            result = msg.result or ""
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--cwd", default=".")
    p.add_argument("--builder", choices=["sonnet", "opus"], help="override the planner's choice")
    p.add_argument("--yes", action="store_true", help="skip the approval prompt")
    a = p.parse_args()

    spec = ask("haiku", REFINE_SYS, a.prompt)
    plan = ask("fable", PLAN_SYS, spec, max_tokens=8000)
    print(f"--- PLAN ---\n{plan}\n")
    if not a.yes and input("Proceed? [y/N] ").strip().lower() != "y":
        return

    m = re.search(r"BUILDER:\s*(sonnet|opus)", plan, re.I)
    builder = a.builder or (m.group(1).lower() if m else "sonnet")
    work = f"SPEC:\n{spec}\n\nPLAN:\n{plan}"
    build_tools = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
    check_tools = ["Read", "Bash", "Glob", "Grep"]

    summary = asyncio.run(agent(builder, BUILD_SYS, work, a.cwd, build_tools))
    verdict = asyncio.run(agent("haiku", VERIFY_SYS, f"{work}\n\nBUILD SUMMARY:\n{summary}", a.cwd, check_tools))
    if "VERDICT: FAIL" in verdict:
        summary = asyncio.run(agent(builder, BUILD_SYS, f"{work}\n\nFix these verification failures:\n{verdict}", a.cwd, build_tools))
        verdict = asyncio.run(agent("haiku", VERIFY_SYS, f"{work}\n\nBUILD SUMMARY:\n{summary}", a.cwd, check_tools))

    status = "Delivered" if "VERDICT: PASS" in verdict else "Delivered with open items"
    today = datetime.date.today().isoformat()
    slug = re.sub(r"[^a-z0-9]+", "-", a.prompt.lower())[:40].strip("-")
    report = pathlib.Path(a.cwd, ".trident", "reports", f"{today}-{slug}.md")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        f"# {a.prompt}\n**Date:** {today} · **Builder:** {builder} · **Status:** {status}\n\n"
        f"## Plan and sources\n{plan}\n\n## Build\n{summary}\n\n## Verification\n{verdict}\n"
    )
    print(f"Status: {status}\nReport: {report}")


if __name__ == "__main__":
    main()
