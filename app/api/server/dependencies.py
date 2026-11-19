"""Dependencies shared by the routers of the api server."""

from typing import Annotated

from fastapi import Depends

from app.api.settings.configs import Config, config


def get_config() -> Config:
    """Return the service's config, replaceable in tests."""
    return config


ConfigDep = Annotated[Config, Depends(get_config)]
