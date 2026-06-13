# Token Guardian

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-2F81F7)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/interface-CLI-00C2FF)](#usage)
[![License: MIT](https://img.shields.io/badge/license-MIT-8CE99A)](#license)
[![Tests](https://img.shields.io/badge/tests-pytest-6EA8FE)](#development)

Token Guardian is a CLI-first guardrail for checking prompt size, context pressure, and estimated cost before you call an LLM.

It helps developers answer three questions quickly:

- how many tokens this prompt will probably use
- how much this request may cost
- whether this prompt is risky for the selected context window

## Why Use Token Guardian?

- catch oversized prompts before they hit the model
- estimate cost before expensive runs
- compare supported models using the same prompt
- clean duplicated or bloated prompt text
- keep simple local observability with SQLite metrics

## Copy-Paste Install

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
token-guardian
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
token-guardian
```

## What the CLI Can Do

- analyze one prompt for one provider/model pair
- compare one prompt across the default supported models
- optimize prompt text by removing duplicates and excess whitespace
- list supported models
- sync the local model catalog snapshot
- inspect local usage metrics

## Usage

### Start here

```bash
token-guardian
```

Running without arguments shows the available flow and the most useful commands to start with.

### Analyze a prompt

```bash
token-guardian analyze \
  --provider anthropic \
  --model claude-sonnet-4 \
  --prompt "Review this architecture proposal and identify risks."
```

### Compare models

```bash
token-guardian compare \
  --prompt "Summarize this technical RFC and list migration risks."
```

### Optimize a prompt

```bash
token-guardian optimize \
  --prompt "Goal: summarize
Goal: summarize


Return bullets only."
```

### List supported models

```bash
token-guardian models
```

### Sync model catalog

```bash
token-guardian sync-models
token-guardian sync-models --provider openai
```

### View local metrics

```bash
token-guardian metrics
```

## Example Output

Typical `analyze` output:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4",
  "input_tokens": 20,
  "estimated_output_tokens": 128,
  "estimated_total_tokens": 148,
  "context_limit": 200000,
  "context_usage_percent": 0.07,
  "estimated_cost_usd": 0.00198,
  "risk_level": "low",
  "context_health_score": 99,
  "cost_score": "$",
  "complexity_score": "Simple",
  "suggestions": [
    "Prompt enxuto e com bom sinal; mantenha foco em objetivo, restricoes e saida."
  ]
}
```

## Supported Providers

Current built-in catalog:

- OpenAI: `gpt-4.1`
- Anthropic: `claude-sonnet-4`, `claude-opus-4`
- Google: `gemini-2.5-pro`, `gemini-2.5-flash`
- OpenRouter: `openai/gpt-4.1`

Each model stores:

- context limit
- input price per 1K tokens
- output price per 1K tokens
- speed estimate
- source URL

The CLI also shows catalog metadata such as:

- `Catalogo atualizado em 2026-06-13`
- the current JSON snapshot path

## Scoring

### Risk level

Based on estimated context usage:

- `low`
- `medium`
- `high`
- `critical`

### Context health score

Range: `0` to `100`

Factors include:

- prompt size
- repeated lines
- repeated vocabulary
- redundant sections

### Cost score

- `$`: very low
- `$$`: low
- `$$$`: medium
- `$$$$`: high

### Complexity score

- `Simple`
- `Medium`
- `Complex`
- `Very Complex`

## Metrics

Token Guardian stores local metrics in SQLite.

Database file:

- `token_guardian.db`

Tracked fields include:

- total requests
- total tokens
- estimated cumulative cost
- top models
- top providers

## Project Structure

```text
token-guardian/
|-- app/
|   |-- cli.py
|   |-- models/
|   |-- providers/
|   |-- services/
|   `-- utils/
|-- docs/
|-- tests/
|-- LICENSE
|-- pyproject.toml
`-- README.md
```

## Development

Run tests:

```bash
pytest
```

Run quality checks:

```bash
ruff check .
black --check .
mypy app
```

## Roadmap

- add richer interactive CLI flows
- expand supported model catalog
- improve prompt optimization heuristics
- add exportable reports
- add model catalog sync support

## License

MIT
