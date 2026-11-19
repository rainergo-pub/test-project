"""Parameters of this service, set directly or loaded from TOML files with dot-notation access to tables."""

from pydantic import BaseModel, ConfigDict


class Param(BaseModel):
    """This service's parameters, as opposed to the environment-driven ``Config``; shared ones are in project_core."""

    model_config = ConfigDict(frozen=True)


param: Param = Param()


if __name__ == "__main__":
    print(param)
