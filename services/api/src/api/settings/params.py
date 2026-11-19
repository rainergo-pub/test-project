"""Parameters of this service, set directly or loaded from TOML files with dot-notation access to tables."""

from pydantic import BaseModel, ConfigDict

from api.settings.dir_or_file_paths import dir_or_file_path
from project_core.utils.special_classes import DotDict


class Param(BaseModel):
    """This service's parameters, as opposed to the environment-driven ``Config``; shared ones are in project_core."""

    model_config = ConfigDict(frozen=True)

    example: DotDict = DotDict.from_toml(path=dir_or_file_path.example_toml)


param: Param = Param()


if __name__ == "__main__":
    print(param.example.section.param_4)
