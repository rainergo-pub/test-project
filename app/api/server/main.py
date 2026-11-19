"""FastAPI application of api."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.server.routers import health
from app.api.settings.configs import config
from app.api.settings.dir_or_file_paths import dir_or_file_path
from app.project_core.settings.log_configs import setup_logging

logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_api: FastAPI) -> AsyncGenerator[None]:
    """Configure logging at startup and release shared resources at shutdown."""
    setup_logging(config=config, log_file=dir_or_file_path.log_file)
    logger.info("Server started")
    yield


api: FastAPI = FastAPI(lifespan=lifespan)
api.include_router(health.router)
