# Trident · OpenAI edition

The Trident pipeline on the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), with the same prompts, licence policy and report format as the other editions.

| Stage | Default model | Reasoning |
|---|---|---|
| Refine | gpt-5.6-luna | low |
| Plan (with web search) | gpt-5.6-sol | high |
| Build · standard | gpt-5.6-terra | medium |
| Build · deep | gpt-5.6-sol | high |
| Verify | gpt-5.6-luna | low |

Every model reference lives in [`trident_openai/models.toml`](trident_openai/models.toml). Override any stage at runtime with `TRIDENT_<STAGE>_MODEL`, for example `TRIDENT_PLAN_MODEL=gpt-5.5`.

## Install and run

```bash
pip install "git+https://github.com/AquarkGR/Trident#subdirectory=editions/openai"
export OPENAI_API_KEY=...
trident-openai --dry-run
trident-openai "build a CLI that converts CSV to Parquet" --cwd ./project
```

| Flag | Effect |
|---|---|
| `--tier standard\|deep` | Override the planner's choice |
| `--yes` | Skip plan and shell-command approvals |
| `--dry-run` | Print the stage configuration |
