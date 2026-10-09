# Trident · Local edition

The Trident pipeline on **one local model**. Instead of switching to bigger models for harder stages, it sizes a single [Qwen3.5](https://huggingface.co/Qwen) model (Apache-2.0) to your RAM. Each stage then spends **reasoning and context as its budget**. No API keys are needed, and your code stays on your machine.

## Budget per stage

| Stage | Reasoning | Output cap | Context share |
|---|---|---|---|
| Refine | off | 1,024 | 25% |
| Plan | on | 8,192 | 100% |
| Build · standard | off | 4,096 | 50% |
| Build · deep | on | 8,192 | 100% |
| Verify | on | 2,048 | 50% |

The planner chooses the tier, so harder work gets more reasoning rather than a larger model. Use `--budget 2` to double every stage's output cap.

## RAM presets

| RAM | Model | Max context |
|---|---|---|
| 8 GB | qwen3.5:4b | 16K |
| 16 GB | qwen3.5:9b | 32K |
| 24 GB | qwen3.5:9b | 64K |
| 32 GB | qwen3.5:35b-a3b (MoE) | 32K |
| 48 GB | qwen3.5:35b-a3b (MoE) | 64K |
| 64 GB | qwen3.5:35b-a3b (MoE) | 128K |
| 128 GB | qwen3.5:122b-a10b (MoE) | 64K |

These are conservative starting points. Tune them in [`trident_local/presets.toml`](trident_local/presets.toml).

## Install and run

Requires [Ollama](https://ollama.com). The model is pulled automatically on first run.

```bash
pip install "git+https://github.com/AquarkGR/Trident#subdirectory=editions/local"
trident-local --ram 16 --dry-run
trident-local "build a CLI that converts CSV to Parquet" --ram 16 --cwd ./project
```

| Flag | Effect |
|---|---|
| `--ram N` | Machine RAM in GB (auto-detected if omitted) |
| `--budget X` | Multiply every stage's output cap |
| `--ctx N` | Override the preset's max context |
| `--tier standard\|deep` | Override the planner's choice |
| `--yes` | Skip plan and shell-command approvals |
| `--dry-run` | Print the model and per-stage budgets |
