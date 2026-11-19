# syntax=docker/dockerfile:1

# --- Build stage: install the locked dependencies and the project into /app/.venv ---
FROM python:3.14-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEFAULT_GROUPS=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-editable

# --- Runtime stage: only the virtual environment, run as a non-root user ---
FROM python:3.14-slim-trixie
RUN groupadd --system --gid 1000 app && useradd --system --uid 1000 --gid app --no-log-init app
WORKDIR /app
# Owned by root: the app can read and run its code and dependencies, but not change them
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" LOG_HANDLERS='["json"]'
# The user app, as a numeric ID, so Kubernetes can verify runAsNonRoot
USER 1000:1000
CMD ["app"]
