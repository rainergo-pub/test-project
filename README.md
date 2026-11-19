# oldws

Old oldws

A uv workspace: each service in `services/` is its own project with its own dependencies, image and Helm chart.

## Setup

```bash
uv sync                  # one .venv with every service, library and the dev tools
for f in env_files/*.env.example; do [ -e "${f%.example}" ] || cp "$f" "${f%.example}"; done   # then fill in
```

## Run

```bash
uv run <service>         # runs one service
```

## Check

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest            # all services; one service: uv run pytest services/<service>
```

## Structure

- `services/<service>/`: one project per service: `pyproject.toml` (its dependencies), `Dockerfile`, the package
  `src/<service>/` and `tests/`. The package holds what only this service uses: `main.py`, `settings/`, and
  `data_structures/` and `utils/` for its own types and helpers.
- `libs/project_core/`: code that every service uses, as its own project without a `Dockerfile`: the shared
  `data_structures/` (such as the enums `Stage`, `LogLevel`, `LoggerType`), `settings/` (the `ProjectConfig` base
  class, shared params and the logging setup) and `utils/` (such as `DotDict`). Every service depends on it; it never
  imports from a service. Code that only some services use can go into a further library: `uv init --lib
  libs/<library>`, then `uv add --package <service> <library>`.
- `tests/` (root): checks across the whole workspace, such as `test_import_boundaries.py`, which fails if a library
  imports a service or a service imports another service.
- `env_files/`: the settings and secrets for local runs: `project.env` for keys that every service uses, and
  `<service>.env` for each service, with the keys only that service uses. Only the `.example` files are committed.
- `deploy/helm/<service-name>/`: one Helm chart per service. Kubernetes names allow no underscores, so the chart
  of a service `order_worker` is `order-worker`.
- `pyproject.toml` (root): the workspace members and the tool settings for all of them; `uv.lock` locks them all.

## Configuration

Each service package has its own `settings/` folder; `libs/project_core/src/project_core/settings/` holds what every
service shares:

- **Config** (`settings/configs.py`, instance `config`): environment-driven, read from `env_files/project.env`, then
  from `env_files/<service>.env` (a later file wins), and environment variables win over both. The service's `Config`
  extends `ProjectConfig`, which defines the fields every service has; logging is controlled by `LOG_LEVEL` (`DEBUG`
  … `CRITICAL`) and `LOG_HANDLERS` (JSON list of `console`, `file`, `json`). Secrets go on the `Config` of the
  service that uses them, so each service gets only its own; only a secret every service uses goes on `ProjectConfig`.
- **Params** (`settings/params.py`, instance `param`): domain parameters, set directly or from the TOML files in
  `settings/param_files/`. Those of every service, such as the logging configuration, are in
  `project_core.settings.params`.
- **Paths** (`settings/dir_or_file_paths.py`, instance `dir_or_file_path`): every filesystem location used by the
  service, including its env files and log file.
- **Logging**: each service's `main()` calls `project_core.settings.log_configs.setup_logging()` with its config and
  log file.

All three are frozen pydantic models: their values can't be changed at runtime. Run the services from the project
root: paths such as `env_files/` and `logs/` (one log file per service, `logs/<service>.log`) are relative to it.

## Docker

```bash
docker compose build
docker compose run --rm <service>    # runs the service once; settings come from env_files/
```

Each image is built from the project root and contains only its service's virtual environment; it runs as user `app`
and logs JSON to stdout. The Python and uv image versions are pinned in each `Dockerfile`.

## Deploy (Helm)

The chart in `deploy/helm/<service-name>/` runs the service once as a Kubernetes Job.

1. Build the image for the cluster's CPU type: most clusters run `linux/amd64`, while a Mac with Apple Silicon
   builds `linux/arm64`; set `platform: linux/amd64` on the service in `docker-compose.yaml` if they differ. Push the
   image to your registry and set `image.repository` and `image.tag` in the chart's `values.yaml`.
2. Create the Secrets from `env_files/`, once for the keys every service uses and once per service, and name both in
   the chart's `values.yaml` (`existingSecrets: [project-env, <service-name>-env]`; where both set a key, the last one
   wins):
   `kubectl create secret generic project-env --from-env-file=env_files/project.env`,
   `kubectl create secret generic <service-name>-env --from-env-file=env_files/<service>.env`.
3. Install: `helm install <service-name> deploy/helm/<service-name>`. A Job can't be changed in place; to run it
   again, run `helm uninstall <service-name>` first.

## Rename or add a service

To rename a service, replace its name in:

1. the folders `services/<service>/` and `services/<service>/src/<service>/`;
2. every file below `services/<service>/` (imports, `pyproject.toml`, `Dockerfile`, the env file and log file names
   in `settings/dir_or_file_paths.py`);
3. `env_files/<service>.env.example` (file name and comment) and the service's entry in `docker-compose.yaml`;
4. the chart folder `deploy/helm/<service-name>/` and the names in its `Chart.yaml` and `values.yaml` (with hyphens).

To add a service, copy an existing one and rename the copy. Then run `uv sync`, and `uv run ruff check --fix .` and
`uv run ruff format .`, because new names can change the order of imports.
