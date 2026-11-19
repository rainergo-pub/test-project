# CLAUDE.md

<!-- Written by /setup-project. Keep it short: it loads in every session. -->

- **What it is:** Python project many
- **Layout:** services `api`, `order_worker`, `json` in `app/api/`, `app/order_worker/`, `app/json/`, shared code in `app/project_core/`
- **Type:** `api`: FastAPI service; `order_worker`, `json`: scripts/CLI
- **Entry points:** `uv run fastapi dev --entrypoint app.api.server.main:api`, `uv run python -m app.order_worker.main`, `uv run python -m app.json.main`

## Project-only preferences

<!-- Apply only to this project and win over the shared rules. -->
- none yet

## Shared standard

@shared/CLAUDE.md
