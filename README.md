# oldsrc

Old oldsrc

## Setup

```bash
uv sync                  # creates .venv with runtime and dev dependencies
cp .env.example .env     # then fill in the secrets
```

## Run

```bash
uv run app
```

## Check

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```

## Configuration

- **Config** (`src/app/settings/configs.py`, instance `config`): environment-driven, read from env vars or `.env` in the working directory.
  Logging is controlled by `LOG_LEVEL` (`DEBUG` … `CRITICAL`) and `LOG_HANDLERS` (JSON list of `console`, `file`, `json`).
- **Params** (`src/app/settings/params.py`, instance `param`): domain parameters, set directly or from the TOML files in `src/app/settings/param_files/`.
- **Paths** (`src/app/settings/dir_or_file_paths.py`, instance `dir_or_file_path`): every filesystem location used by the app.

All three are frozen pydantic models: their values can't be changed at runtime.

## Docker

```bash
docker compose build
docker compose run --rm app     # runs the app once; settings come from .env
```

The image contains only the virtual environment, runs as user `app` and logs JSON to stdout. The Python and uv
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
