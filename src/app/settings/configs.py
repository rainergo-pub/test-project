"""System-wide configuration loaded from environment variables and the env files."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.data_structures.enums import LoggerType, LogLevel, Stage
from app.settings.dir_or_file_paths import dir_or_file_path


class Config(BaseSettings):
    """Environment-driven system configuration; env vars take precedence over the env files."""

    model_config = SettingsConfigDict(
        env_file=dir_or_file_path.env_files,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
    )

    stage: Stage = Stage.DEV
    log_level: LogLevel = LogLevel.INFO
    log_handlers: tuple[LoggerType, ...] = (LoggerType.CONSOLE,)

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None


config: Config = Config()


if __name__ == "__main__":
    # SecretStr fields print as '**********'; use get_secret_value() to read the actual value.
    print(config.openai_api_key)
