# CLAUDE.md

<!-- Written by /setup-project. Keep it short: it loads in every session. -->

- **What it is:** Tools to reconcile warehouse stock counts, for the warehouse team
- **Layout:** one package in `app/` (flat, not installed), scripts in `scripts/`, notebooks in `notebooks/`
- **Type:** scripts/CLI
- **Entry points:** `uv run python -m app.cli <old.csv> <new.csv>`
- **External services:** the warehouse API (`WAREHOUSE_TOKEN`)

## Project-only preferences

<!-- Apply only to this project and win over the shared rules. -->
- none yet

## Shared standard

@shared/CLAUDE.md
