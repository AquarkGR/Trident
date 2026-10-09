# Trident

Prompt, plan, build with the right Claude model at each step.

**Haiku** refines the request. **Fable** researches open, permissively-licensed prior work and plans. **Sonnet** builds, or **Opus** for complex work. **Haiku** independently verifies. Every run ends with a one-page report in `.trident/reports/`.

## Usage

```
/trident:ship <what you want built> [--yes] [--pr]
```

- `--yes` skips the approval brief.
- `--pr` opens a pull request with the report as its description (requires an authenticated `gh`).

## Components

| Type | Name | Model |
|---|---|---|
| Skill | `ship` | Orchestrates the run |
| Agent | `refiner` | Haiku |
| Agent | `planner` | Fable (with web search) |
| Agent | `builder` | Sonnet, or Opus when the planner selects it |
| Agent | `verifier` | Haiku (read-only, runs tests) |

## Policies

- **Licences:** MIT, Apache-2.0, BSD, ISC, Unlicense, CC0, PSF and Zlib only.
- **Grounding:** cited sources must have been opened, and APIs are checked against installed versions.
- **Approval:** you approve a short brief before anything is built, unless you pass `--yes`.

Full documentation: https://github.com/AquarkGR/Trident
