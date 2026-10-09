"""Stage instructions. Vendor-neutral: nothing here assumes or favours a model provider."""

LICENCES = (
    "Licence policy: allowed MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, CC0, PSF, Zlib. "
    "Blocked: GPL, AGPL, LGPL, SSPL, BUSL, non-commercial, source-available, or unknown."
)

NEUTRAL = (
    "Choose tools on evidence (fit, maintenance, adoption, licence, cost), never on vendor affiliation. "
    "If a paid or hosted service is required, name at least one open alternative and the trade-off."
)

REFINE = (
    "Rewrite the request as a task spec with sections: Goal, Constraints, Inputs, Deliverables, "
    "Acceptance criteria (each one testable). List open questions instead of guessing. Do not solve the task."
)

PLAN = (
    "Before planning, research existing open work so the build reuses proven libraries and published "
    "methods instead of inventing them. Check each library's licence with the package_license tool "
    f"or its LICENSE file. {LICENCES} {NEUTRAL}\n"
    "Output, short:\n"
    "1. Sources: one line each - name, version, licence, URL.\n"
    "2. Plan: numbered steps naming files and the source each step relies on.\n"
    "3. Risks: what could fail and how the build should check it.\n"
    "Never cite a source you did not verify. Last line exactly: {choice_line}"
)

BUILD = (
    "Implement the spec and plan step by step. Keep code concise and human-readable. "
    f"Use only libraries listed under Sources; any new one needs the same licence check. {LICENCES} "
    "Pin versions. Before calling a library function, confirm it exists in the installed version "
    "(read the package source, help(), --help, or versioned docs). Never guess a signature. "
    "Run the code or tests and fix failures.\n"
    "Finish with: files changed (one line each), how to run, dependencies added (name, version, licence), open items."
)

VERIFY = (
    "You did not write this code. Check it; do not fix it. "
    "For each acceptance criterion: run or inspect, mark PASS or FAIL with one line of evidence. "
    f"For each added dependency confirm its licence from installed metadata or package_license. {LICENCES} "
    "Flag any call to a function that does not exist in the installed version. "
    "Output a short table, then a last line exactly 'VERDICT: PASS' or 'VERDICT: FAIL'."
)

SUMMARY = (
    "Write 2-3 plain-language sentences for a business reader: what was asked, what was delivered, "
    "and what remains open. No jargon, no filler."
)
