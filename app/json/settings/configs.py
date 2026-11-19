"""Configuration of this service, loaded from environment variables and its env files."""

from pydantic_settings import SettingsConfigDict

from app.json.settings.dir_or_file_paths import dir_or_file_path
from app.project_core.settings.configs import ProjectConfig


class Config(ProjectConfig):
    """The project's fields plus this service's own; env vars take precedence over the env files."""

    model_config = SettingsConfigDict(env_file=dir_or_file_path.env_files)


config: Config = Config()


if __name__ == "__main__":
    print(config.log_level)
