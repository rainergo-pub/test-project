"""Configuration of this service, loaded from environment variables and its env files."""

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from project_core.settings.configs import ProjectConfig
from worker.settings.dir_or_file_paths import dir_or_file_path


class Config(ProjectConfig):
    """The project's fields plus this service's own; env vars take precedence over the env files."""

    model_config = SettingsConfigDict(env_file=dir_or_file_path.env_files)

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None


config: Config = Config()


if __name__ == "__main__":
    # SecretStr fields print as '**********'; use get_secret_value() to read the actual value.
    print(config.openai_api_key)
