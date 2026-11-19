# inventory-tools

Reconciles warehouse stock counts: it compares two stock exports and lists every item whose count changed. For the
warehouse team.

## Requirements

- uv, check with `uv --version`. uv also installs the Python version from `.python-version` (3.12).

## Setup

1. Install the dependencies; this creates `.venv/` and installs nothing of the project itself:
   ```bash
   uv sync
   ```
2. Create your environment file from the example and fill in the keys:
   ```bash
   cp .env.example .env
   ```

## Configuration

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `STAGE` | `dev` | Deployment stage |
| `LOG_LEVEL` | `INFO` | Log level, `DEBUG` … `CRITICAL` |
| `LOG_HANDLERS` | `["console"]` | Where logs go: JSON list of `console`, `file`, `json` |

## Usage

From the project root, compare an old and a new export (CSV files with the columns `sku` and `count`):

```bash
uv run python -m app.cli data/old.csv data/new.csv
```

Each output line is a SKU and the change of its count.

## What's where

| Path | Contains |
| --- | --- |
| `app/stock.py` | Reading the exports and computing the differences |
| `app/cli.py` | The command-line entry point |
| `app/settings/` | Configuration, paths and parameters |
| `scripts/fetch_counts.py` | Downloads the current counts from the warehouse API |
| `notebooks/` | Data exploration |
| `tests/` | The tests |

## Development

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```
