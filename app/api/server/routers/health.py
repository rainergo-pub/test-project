"""Health and stage endpoints of the api server."""

from fastapi import APIRouter

from app.api.server.dependencies import ConfigDep

router: APIRouter = APIRouter(tags=["health"])


@router.get("/health")
def read_health() -> dict[str, str]:
    """Answer the container healthcheck."""
    return {"status": "ok"}


@router.get("/stage")
def read_stage(*, config: ConfigDep) -> dict[str, str]:
    """Return the stage the server runs in."""
    return {"stage": config.stage}
