"""Parameters shared by every service, set directly or loaded from TOML files with dot-notation access to tables."""

from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict

from app.project_core.settings.dir_or_file_paths import dir_or_file_path
from app.project_core.utils.special_classes import DotDict


class Param(BaseModel):
    """Parameters every service uses, as opposed to the environment-driven ``ProjectConfig``."""

    model_config = ConfigDict(frozen=True)

    timezone: ZoneInfo = ZoneInfo("Europe/Berlin")
    logging: DotDict = DotDict.from_toml(path=dir_or_file_path.logging_toml)


param: Param = Param()


if __name__ == "__main__":
    print(param.timezone)
