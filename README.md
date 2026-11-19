# one

Python project one

## Setup

```bash
uv sync                  # creates .venv with the dependencies; the project itself is not installed
cp .env.example .env     # then fill in the secrets
```

## Run

From the project root:

```bash
uv run python -m app.main
```

## Structure

- `app/`: the code, run from the project root, never installed (`package = false` in `pyproject.toml`).
- `tests/`: the tests, in the same folders as the code they test.
- `experiments/`: experiments and data exploration, scripts and notebooks. They may import from `app`, but `app`
  never imports from them. Run a script that imports from `app` as a module from the project root,
  `uv run python -m experiments.<name>`; run such a notebook in the IDE with the project root on the path (PyCharm
  does this by default; in VS Code set `"jupyter.notebookFileRoot": "${workspaceFolder}"`).
- `data/`, `logs/`: data and log files, not in git.
- `deploy/helm/app/`: the Helm chart.

## Check

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```

## Configuration

- **Config** (`app/settings/configs.py`, instance `config`): environment-driven, read from env vars or `.env` in the working directory.
  Logging is controlled by `LOG_LEVEL` (`DEBUG` … `CRITICAL`) and `LOG_HANDLERS` (JSON list of `console`, `file`, `json`).
- **Params** (`app/settings/params.py`, instance `param`): domain parameters, set directly or from the TOML files in `app/settings/param_files/`.
- **Paths** (`app/settings/dir_or_file_paths.py`, instance `dir_or_file_path`): every filesystem location used by the app.

All three are frozen pydantic models: their values can't be changed at runtime.

## Docker

```bash
docker compose build
docker compose run --rm app     # runs the app once; settings come from .env
```

The image contains only the virtual environment and `app/`, runs `python -m app.main` as user `app` and logs JSON
to stdout. The Python and uv
image versions are pinned in the `Dockerfile`.

## Deploy (Helm)

The chart in `deploy/helm/app/` runs the app once as a Kubernetes Job.

1. Build the image for the cluster's CPU type: most clusters run `linux/amd64`, while a Mac with Apple Silicon
   builds `linux/arm64`; set `platform: linux/amd64` on the service in `docker-compose.yaml` if they differ. Push the
   image to your registry and set `image.repository` and `image.tag` in `deploy/helm/app/values.yaml`.
2. Create a Secret from `.env` and name it in `values.yaml`:
   `kubectl create secret generic app-env --from-env-file=.env`, then `existingSecrets: [app-env]`.
3. Install: `helm install app deploy/helm/app`. A Job can't be changed in place; to run it again, run
   `helm uninstall app` first.
