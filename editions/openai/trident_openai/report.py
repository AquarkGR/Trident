"""One-page, business-style run report for maintainers."""
import datetime
import pathlib
import re


def write_report(cwd: str, request: str, summary: str, engine: str, spend: dict,
                 plan: str, build: str, verdict: str) -> pathlib.Path:
    today = datetime.date.today().isoformat()
    status = "Delivered" if "VERDICT: PASS" in verdict else "Delivered with open items"
    slug = re.sub(r"[^a-z0-9]+", "-", request.lower())[:40].strip("-") or "run"
    path = pathlib.Path(cwd, ".trident", "reports", f"{today}-{slug}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    spend_rows = "\n".join(f"| {stage} | {detail} |" for stage, detail in spend.items())
    path.write_text(
        f"# {request}\n"
        f"**Date:** {today} · **Engine:** {engine} · **Status:** {status}\n\n"
        f"## Summary\n{summary.strip()}\n\n"
        f"## Plan and sources\n{plan.strip()}\n\n"
        f"## Build\n{build.strip()}\n\n"
        f"## Verification\n{verdict.strip()}\n\n"
        f"## Spend\n| Stage | Budget used |\n|---|---|\n{spend_rows}\n"
    )
    return path
