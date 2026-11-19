"""Domain parameters, set directly or loaded from TOML files with dot-notation access to tables."""

from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict

from app.settings.dir_or_file_paths import dir_or_file_path
from app.utils.special_classes import DotDict


class Param(BaseModel):
    """Domain parameters, as opposed to the environment-driven ``Config``."""

    model_config = ConfigDict(frozen=True)

    timezone: ZoneInfo = ZoneInfo("Europe/Berlin")
    example: DotDict = DotDict.from_toml(path=dir_or_file_path.example_toml)
    logging: DotDict = DotDict.from_toml(path=dir_or_file_path.logging_toml)


param: Param = Param()


if __name__ == "__main__":
    print(param.example.section.param_4)
