# syntax=docker/dockerfile:1

# --- Build stage: install the locked dependencies into /app/.venv and precompile the code ---
FROM python:3.15-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEFAULT_GROUPS=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked
COPY app /app/app
# The root filesystem is read-only at runtime, so Python can't write .pyc files there
RUN python -m compileall -q /app/app

# --- Runtime stage: the virtual environment and the code, run as a non-root user ---
FROM python:3.15-slim-trixie
RUN groupadd --system --gid 1000 app && useradd --system --uid 1000 --gid app --no-log-init app
WORKDIR /app
# Owned by root: the app can read and run its code and dependencies, but not change them
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
ENV PATH="/app/.venv/bin:$PATH" LOG_HANDLERS='["json"]'
# The user app, as a numeric ID, so Kubernetes can verify runAsNonRoot
USER 1000:1000
CMD ["python", "-m", "app.main"]
