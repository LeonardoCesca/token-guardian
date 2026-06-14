# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [0.1.1] - 2026-06-14

### Added

- CLI screenshot asset for README and PyPI project presentation.

### Changed

- Translated the user-facing CLI experience to pt-BR, including menu text, labels, and result views.
- Updated the README preview so the published package page better reflects the current terminal interface.

## [0.1.0] - 2026-06-13

### Added

- CLI-first `token-guardian` command for prompt preflight workflows.
- Interactive terminal menu with guided flows for `analyze`, `compare`, `optimize`, `models`, `sync-models`, and `metrics`.
- JSON-backed model catalog with provider adapters for OpenAI, Anthropic, Google, and OpenRouter.
- `sync-models` command to refresh the local catalog snapshot while preserving provider metadata.
- Local SQLite observability for requests, token usage, cost estimates, top models, and top providers.
- Premium terminal presentation using `rich` panels, tables, cards, quick actions, and onboarding hints.
- MIT license file for public distribution.
- Packaging metadata for PyPI release and Trusted Publishing workflow for GitHub Actions.

### Changed

- Repositioned the project as CLI-only instead of MCP/API-first.
- Simplified the interactive prompt flow so `Enter` sends the prompt directly.
- Made output token estimation automatic in the interactive flow.
- Upgraded release metadata with project URLs, keywords, and classifiers.

### Removed

- MCP server entrypoints and MCP-focused distribution path.
- FastAPI and Docker release path from the main product surface.
- Legacy command patterns that no longer match the CLI-first product direction.
