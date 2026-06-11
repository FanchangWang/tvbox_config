# TVBox Config — Project Guide

## Overview

TVBox source checker and JSON generator. Fetches TVBox source URLs, decrypts
encrypted sources (AES-CBC / base64), validates content, and generates
`tvbox.json` / `my.json` output files. Runs daily via GitHub Actions.

## Tech Stack

| Category        | Choice                         |
| --------------- | ------------------------------ |
| Python          | 3.12+                          |
| Package manager | `uv` (no pip/poetry/conda)     |
| Lint + Format   | `ruff`                         |
| Type check      | `ty`                           |
| Test            | `pytest` + `pytest-cov`        |
| HTTP mock       | `respx`                        |
| Build           | `hatchling`                    |

## Project Structure

```
tvbox_config/
├── src/tvbox_config/          # Package source
│   ├── __init__.py            # Public API exports
│   ├── app.py                 # Main App class, CLI entry
│   ├── _check.py              # `uv run check` entry (ruff + ty)
│   ├── decrypt.py             # AES-CBC / base64 decryption functions
│   ├── http_client.py         # httpx wrapper with okhttp UA
│   ├── json_builder.py        # Module-level functions for JSON output
│   ├── logger.py              # logging setup to stderr
│   ├── models.py              # Source / AvailableSource dataclasses
│   └── source_manager.py      # YAML config load/save
├── config/
│   ├── sources.yaml           # Source definitions
│   └── history.yaml           # Last successful state
├── dist/                      # Generated JSON output
├── tests/                     # pytest tests
├── .github/workflows/         # CI: daily_update.yml
├── pyproject.toml
└── AGENTS.md
```

## Commands

```bash
uv sync                  # Install / sync dependencies
uv run tvbox-config      # Main: check sources, generate JSON
uv run check             # Run ruff check + ruff format --check + ty check
uv run ruff check .      # Lint only
uv run ruff format .     # Format only
uv run ty check          # Type check only
uv run pytest            # Run tests with coverage
uv add <package>         # Add production dependency
uv add --dev <package>   # Add dev dependency
```

## Code Conventions

### Structure
- **src-layout** under `src/tvbox_config/`
- Stateless transformations → module-level functions (`decrypt.py`, `json_builder.py`, `logger.py`, `_check.py`)
- Objects with state/lifecycle → class (`HttpClient`, `SourceManager`, `App`)
- Data containers → `@dataclass` with `to_dict()` / `from_dict()` (`models.py`)

### Styling (enforced by ruff)
- Target Python 3.12, line length 100
- Double quotes for strings
- Spaces for indentation
- Imports: stdlib → third-party → local (separated by blank lines)
- Annotate return types on all functions
- Use `ClassVar` for class-level constants
- Use `Self` return type for `@classmethod`
- No comments in code (except docstrings in `pyproject.toml` config)

### Formatting (ruff)
```bash
ruff format . && ruff check . --fix
```

### Logging
- `logging` via `get_logger()` from `logger.py`
- Format: `[HH:MM:SS] [LEVEL] message`
- Outputs to stderr
- `logger.info()` for milestones
- `logger.debug()` for per-URL progress
- `logger.error()` for failures
- Log patterns for sources:
  - Encrypted: start with `⏳ 解密数据源: {name} - {url}`
  - Not encrypted: start with `⏳ 检查数据源: {name} - {url}`
  - Success: `✅ 可用数据源: {name} - {url}`
  - All URLs exhausted: `🚫 不可用数据源: {name}`

### HTTP Client
- UA: `okhttp/4.12.0`
- `follow_redirects=True`
- Connect timeout: 5s, read timeout: 30s
- On any `httpx.HTTPError` → return `None`

### Decryption (source.encrypted == true)
- Local Python decryption first:
  1. Fetch raw content from source URL
  2. If already JSON (dict with `spider` + `sites` keys) → skip decryption
  3. If contains `xxxxxxxx**` pattern → try base64 decode
  4. If starts with `2423` → try AES-CBC decrypt
- Fallback: try remote decrypt API endpoints (`DECRYPT_URLS`)

### Decryption API URLs (defined as `App.DECRYPT_URLS`)
1. `https://feiyangdigital.v1.mk/api/jiemi.php?url=`
2. `https://www.饭太硬.net/jm/jiemi.php?url=`

## Dependencies

### Production
- `dirtyjson` — lenient JSON parser
- `httpx` — HTTP client
- `pyyaml` — YAML config parser
- `pycryptodome` — AES-CBC decryption

### Dev
- `ruff` — linter + formatter
- `ty` — type checker
- `pytest` + `pytest-cov` — testing + coverage
- `respx` — HTTP mocking for tests

## GitHub Actions

Runs daily at 03:00 UTC via `.github/workflows/daily_update.yml`:

1. Checkout + install uv + Python 3.12
2. `uv sync`
3. `uv run tvbox-config`
4. If `dist/` or `config/` changed → commit and push

## Content Validation (JSON)

A source is valid when parsing with `dirtyjson` yields a dict that contains
**both** non-empty `"spider"` and `"sites"` keys.

## Testing

Tests go in `tests/`, mirroring source structure:

```bash
uv run pytest -v -s    # verbose, no capture
uv run pytest          # default (with coverage)
```

Use `respx` to mock HTTP when testing network-dependent code.
