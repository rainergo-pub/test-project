# Deviations from the shared standard

Where this project deliberately does something differently from a shared rule, because the user decided so. These
entries win over the shared rules within their scope: follow them, also in new code, and never report or "fix" them.
Entry format and when to add an entry: see `.claude/shared/rules/deviations-format.md`.

### The project stays a uv workspace
- **Date:** 2026-11-19
- **Overrides:** `CLAUDE.md`: the package is `app/` in the project root (the flat layout), not installed
- **Scope:** `**`
- **Instead:** Services in `services/<service>/src/<service>/`, shared code in `libs/project_core/`, installed by uv.
- **Why:** The user declined the move in /adopt-code-structure; the workspace keeps working as it is.
