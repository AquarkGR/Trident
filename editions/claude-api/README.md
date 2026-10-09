# Trident · Claude API edition

The Trident pipeline as a single Python script on the Claude API and the Claude Agent SDK, for CI or your own tooling. It mirrors the plugin's stages: Haiku refines, Fable plans, Sonnet or Opus builds, Haiku verifies, and a report is written to `.trident/reports/`.

```bash
pip install anthropic claude-agent-sdk
export ANTHROPIC_API_KEY=...
python editions/claude-api/trident.py "your request" --cwd ./project [--builder opus] [--yes]
```

Model IDs are in the `MODELS` dict at the top of [`trident.py`](trident.py).

Unlike the plugin, this script does not do live web research while planning, so its source citations come from the model's own knowledge. For research-grounded plans, use the [Claude Code plugin](../../README.md).
