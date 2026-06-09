# Architecture

## Components

- `app/routes`: FastAPI endpoints for REST consumption.
- `app/services`: analysis, optimization, metrics, and SQLite persistence.
- `app/providers`: extensible model catalog and provider registry.
- `app/utils`: token estimation heuristics and prompt scoring helpers.
- `app/mcp_server.py`: MCP tool surface for compatible clients over `stdio`.

## Request Flow

1. Client sends prompt payload to REST or MCP tool.
2. Provider registry resolves model pricing and context metadata.
3. Token estimator calculates input and output estimates.
4. Analyzer computes usage, cost, risk, health, and complexity scores.
5. Metrics service persists totals in SQLite.
6. Response is returned with optimization hints.
