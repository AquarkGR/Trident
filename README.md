# Trident

**Prompt, plan, build.** A Claude Code plugin that routes each step of a task to the right Claude model, grounds the build in open, permissively-licensed work, and ends every run with a one-page report your team can read.

```
/trident:ship build a CLI that converts CSV to Parquet with a --compression flag
```

| Stage | Model | What it does |
|---|---|---|
| **Refine** | Haiku | Turns a rough request into a spec with testable acceptance criteria |
| **Plan** | Fable | Researches existing libraries and papers, checks licences, writes a cited plan, picks the builder |
| **Build** | Sonnet, or Opus for complex work | Implements the plan and checks every API against the installed version before using it |
| **Verify** | Haiku | Independently tests the acceptance criteria and dependency licences, and sends failures back once |
| **Report** | — | Writes `.trident/reports/<date>-<task>.md`: summary, decisions, sources, verification, changes, risks |

## Why Trident

- **Grounded, not guessed.** The planner cites only sources it has opened. The builder confirms function signatures in the installed package. A separate verifier, which did not write the code, checks the result.
- **Licence-safe by default.** Dependencies must be MIT, Apache-2.0, BSD, ISC, Unlicense, CC0, PSF or Zlib. GPL-family, SSPL, BUSL, non-commercial and unknown licences are blocked.
- **People stay in charge.** You approve a short brief before anything is built. Reports read as plain business updates and double as pull-request descriptions.
- **Spend goes where it matters.** Fast models handle the routine stages. The frontier model plans, and Opus is used only when the planner judges the work complex.

## Install

Requires [Claude Code](https://code.claude.com).

```bash
claude plugin marketplace add AquarkGR/Trident
claude plugin install trident@aquark
```

Update later with `claude plugin update trident@aquark`.

## Use

In any Claude Code session:

```
/trident:ship <what you want built>
```

| Option (add to the request) | Effect |
|---|---|
| `--yes` | Skip the approval brief |
| `--pr` | Open a pull request with the report as its description (requires an authenticated `gh`) |

Example: `/trident:ship add input validation to the upload endpoint --pr`

## Example run

A real run of `/trident:ship build a small Python CLI csv2parquet … plus a test using sample.csv` took about 4 minutes:

- **Plan:** the planner reviewed an existing Apache-2.0 csv2parquet project, used none of its code, and chose `pyarrow` alone to keep dependencies minimal.
- **Build:** Sonnet built a packaged CLI with 10 passing tests.
- **Verify:** the verifier confirmed each criterion with evidence, including round-tripped values and the codec reported by Parquet metadata.

Read the full report: [examples/csv2parquet-report.md](examples/csv2parquet-report.md)

## Customize

Each stage is one Markdown file in [`plugins/trident/agents/`](plugins/trident/agents/). Edit its prompt, tools or `model`. The orchestration and report template live in [`plugins/trident/skills/ship/SKILL.md`](plugins/trident/skills/ship/SKILL.md). Bump `version` in [`plugin.json`](plugins/trident/.claude-plugin/plugin.json) when you change behaviour.

## Other editions

The same pipeline, with the same neutral prompts, licence policy and report format, is available outside Claude Code:

| Edition | Runs on | Folder |
|---|---|---|
| Claude API | Claude API and Agent SDK, for CI or your own tooling | [`editions/claude-api`](editions/claude-api) |
| OpenAI | OpenAI Agents SDK | [`editions/openai`](editions/openai) |
| Local | One local Qwen model on Ollama, sized to your RAM. Stages spend reasoning and context as budget instead of switching to larger models | [`editions/local`](editions/local) |

## Repository layout

```
.claude-plugin/marketplace.json   Marketplace catalogue (lists the plugin)
plugins/trident/                  The Claude Code plugin
  agents/                         refiner, planner, builder, verifier
  skills/ship/SKILL.md            /trident:ship orchestration and report template
editions/                         API, OpenAI and local editions
examples/                         Reports from real runs
```

## Contributing

Issues and pull requests are welcome. Before opening a PR:

```bash
claude plugin validate --strict ./plugins/trident
```

CI validates the plugin and dry-runs every edition on each push.

## License

MIT © Aquark. Trident is an independent project and is not affiliated with Anthropic, OpenAI or Alibaba Cloud.
