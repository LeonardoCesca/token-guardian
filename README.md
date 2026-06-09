# Token Guardian MCP

Token Guardian MCP is an open-source MCP server that gives developers observability into LLM prompt usage before execution.

It estimates:

- Input tokens
- Output tokens
- Total tokens
- Context window usage
- Estimated cost
- Context overflow risk
- Prompt optimization opportunities
- Context health and complexity scores

It is designed for tools such as Claude Code, Codex CLI, Cursor, Windsurf, Continue.dev, VS Code, and any compatible MCP client.

## Features

- `analyze_prompt`: inspect one provider/model pair before sending a prompt.
- `compare_models`: compare token impact and estimated cost across multiple models.
- `optimize_prompt`: remove obvious prompt bloat and duplicated instructions.
- REST API with FastAPI for dashboards or integrations.
- SQLite metrics persistence for request, token, and cost tracking.
- Extensible provider registry for adding more models later.

## Supported Providers

Initial catalog:

- OpenAI: `gpt-4.1`
- Anthropic: `claude-sonnet-4`, `claude-opus-4`
- Google: `gemini-2.5-pro`, `gemini-2.5-flash`
- OpenRouter: `openai/gpt-4.1`

Each model stores:

- Context limit
- Input price per 1K tokens
- Output price per 1K tokens
- Speed estimate

## Project Structure

```text
token-guardian-mcp/
├── app/
│   ├── main.py
│   ├── mcp_server.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── providers/
│   └── utils/
├── tests/
├── docs/
├── README.md
├── pyproject.toml
└── Dockerfile
```

## Local Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## Run The REST API

```bash
uvicorn app.main:app --reload
```

Available endpoints:

- `GET /health`
- `POST /api/analyze`
- `POST /api/compare`
- `POST /api/optimize`
- `GET /metrics`

## Run As MCP Server

```bash
python -m app.mcp_server
```

Or, after installation:

```bash
token-guardian-mcp
```

The MCP transport is `stdio`, which works well for local MCP-compatible clients.

## MCP Configuration Examples

### Codex CLI

```json
{
  "mcpServers": {
    "token-guardian": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "C:\\Users\\you\\token-guardian-mcp"
    }
  }
}
```

### Claude Code / Generic MCP Client

```json
{
  "mcpServers": {
    "token-guardian": {
      "command": "token-guardian-mcp"
    }
  }
}
```

## Example Usage

### `analyze_prompt`

Input:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4",
  "prompt": "Review this architecture proposal and identify risks."
}
```

Output:

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

### `compare_models`

Input:

```json
{
  "prompt": "Summarize this technical RFC and list migration risks."
}
```

### `optimize_prompt`

Input:

```json
{
  "prompt": "Goal: summarize\nGoal: summarize\n\n\nReturn bullets only."
}
```

## Metrics Dashboard Endpoint

The project exposes `GET /metrics` backed by SQLite.

Tracked metrics:

- `total_requests`
- `total_tokens`
- `total_cost_estimated`
- `top_models`
- `top_providers`

Database file:

- `token_guardian.db`

## Scoring Model

### Context Health Score

Range: `0` to `100`

Factors:

- Prompt size
- Repeated lines
- Repeated vocabulary
- Redundant sections

### Cost Score

- `$`: very low
- `$$`: low
- `$$$`: medium
- `$$$$`: high

### Prompt Complexity Score

- `Simple`
- `Medium`
- `Complex`
- `Very Complex`

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

Current suite covers:

- Token estimation
- Cost calculation
- Model comparison
- Context health scoring
- Complexity scoring
- Metrics persistence
- Prompt optimization

## Quality

```bash
ruff check .
black --check .
mypy app
```

## Docker

Build:

```bash
docker build -t token-guardian-mcp .
```

Run API:

```bash
docker run --rm -p 8000:8000 token-guardian-mcp
```

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Screenshots

Suggested screenshots to add before publishing:

- FastAPI Swagger page
- MCP client calling `analyze_prompt`
- Metrics endpoint output

## Roadmap

- Add provider-native tokenizers
- Add richer optimization rewrites
- Add historical dashboards
- Add exportable reports
- Add benchmark-based speed estimates

## License

MIT
