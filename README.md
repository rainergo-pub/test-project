# many

Python project many

One package `app/` with a subpackage per service and `app/project_core/` for what every service uses. Each service
has its own dependencies, image and Helm chart.

## Setup

```bash
uv sync                  # one .venv with the dependencies of every service and the dev tools; app/ is not installed
for f in env_files/*.env.example; do [ -e "${f%.example}" ] || cp "$f" "${f%.example}"; done   # then fill in
```

## Run

From the project root:

```bash
uv run python -m app.<service>.main     # runs order_worker or json once
uv run fastapi dev --entrypoint app.api.server.main:api --port 8000   # the api server, with reload
```

## Check

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest            # all services; one service: uv run pytest tests/<service>
```

## Structure

- `app/`: the code, run from the project root, never installed (`package = false` in `pyproject.toml`).
  - `app/<service>/`: what only this service uses: `main.py`, `settings/`, and `data_structures/` and `utils/` for
    its own types and helpers.
  - `app/project_core/`: what every service uses: the shared `data_structures/` (such as the enums `Stage`,
    `LogLevel`, `LoggerType`), `settings/` (the `ProjectConfig` base class, shared params and the logging setup) and
    `utils/` (such as `DotDict`). It never imports from a service, and a service never imports from another one.
- `tests/`: `tests/<service>/` and `tests/project_core/`, in the same folders as the code they test, and checks
  across the whole project, such as `test_import_boundaries.py`, which fails if `project_core` imports a service, a
  service imports another service, or either imports code in `app/` outside `project_core` and the services, which
  no image contains.
- `pyproject.toml`: the dependencies every service uses in `dependencies`, those of one service in the dependency
  group of the same name (`uv add --group <service> <pkg>`), and the tool settings; `uv.lock` locks them all.
- `docker/<service>.Dockerfile`: one image per service.
- `env_files/`: the settings and secrets for local runs: `project.env` for keys that every service uses, and
  `<service>.env` for each service, with the keys only that service uses. Only the `.example` files are committed.
- `deploy/helm/<service-name>/`: one Helm chart per service. Kubernetes names allow no underscores, so the chart
  of a service `order_worker` is `order-worker`.
- `experiments/`: experiments and data exploration, scripts and notebooks. They may import from `app`, but `app`
  never imports from them. Run a script that imports from `app` as a module from the project root,
  `uv run python -m experiments.<name>`; run such a notebook in the IDE with the project root on the path (PyCharm
  does this by default; in VS Code set `"jupyter.notebookFileRoot": "${workspaceFolder}"`).
- `data/`, `logs/`: data and log files, not in git.

## Configuration

Each service has its own `settings/` folder; `app/project_core/settings/` holds what every service shares:

- **Config** (`settings/configs.py`, instance `config`): environment-driven, read from `env_files/project.env`, then
  from `env_files/<service>.env` (a later file wins), and environment variables win over both. The service's `Config`
  extends `ProjectConfig`, which defines the fields every service has; logging is controlled by `LOG_LEVEL` (`DEBUG`
  … `CRITICAL`) and `LOG_HANDLERS` (JSON list of `console`, `file`, `json`). Secrets go on the `Config` of the
  service that uses them, so each service gets only its own; only a secret every service uses goes on `ProjectConfig`.
- **Params** (`settings/params.py`, instance `param`): domain parameters, set directly or from the TOML files in
  `settings/param_files/`. Those of every service, such as the logging configuration, are in
  `app.project_core.settings.params`.
- **Paths** (`settings/dir_or_file_paths.py`, instance `dir_or_file_path`): every filesystem location used by the
  service, including its env files and log file.
- **Logging**: each service's `main()` calls `app.project_core.settings.log_configs.setup_logging()` with its config
  and log file.

All three are frozen pydantic models: their values can't be changed at runtime. Run the services from the project
root: paths such as `env_files/` and `logs/` (one log file per service, `logs/<service>.log`) are relative to it.

## Docker

```bash
docker compose build
docker compose run --rm <service>    # runs the service once; settings come from env_files/
```

Each image is built from the project root with `docker/<service>.Dockerfile`. It contains the dependencies of
`pyproject.toml` plus only its service's dependency group, and of `app/` only `app/project_core/` and its own
`app/<service>/`; it runs `python -m app.<service>.main` as user
`app` and logs JSON to stdout. The Python and uv image versions are pinned in each Dockerfile.

## Deploy (Helm)

The chart in `deploy/helm/<service-name>/` runs the service once as a Kubernetes Job; the chart of `api` runs it as
a Deployment with a Service.

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

1. the folders `app/<service>/` and `tests/<service>/`, and every import of `app.<service>` in them;
2. `settings/dir_or_file_paths.py` of the service (the env file and log file names);
3. `pyproject.toml` (its dependency group and the entry in `default-groups`);
4. `docker/<service>.Dockerfile` (file name, `--group` and the module in `CMD`);
5. `env_files/<service>.env.example` (file name and comment) and the service's entry in `docker-compose.yaml`;
6. the chart folder `deploy/helm/<service-name>/` and the names in its `Chart.yaml` and `values.yaml` (with hyphens).

The name `project_core` is taken. To add a service, copy an existing one and rename the copy. Then run `uv sync`, and
`uv run ruff check --fix .` and `uv run ruff format .`, because new names can change the order of imports.
