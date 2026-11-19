"""Configuration fields every service has; each service's ``Config`` extends ``ProjectConfig`` with its env files."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.project_core.data_structures.enums import LoggerType, LogLevel, Stage


class ProjectConfig(BaseSettings):
    """Environment-driven fields of every service; it has no instance, because only a service knows its env files."""

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_ignore_empty=True, extra="ignore", frozen=True)

    stage: Stage = Stage.DEV
    log_level: LogLevel = LogLevel.INFO
    log_handlers: tuple[LoggerType, ...] = (LoggerType.CONSOLE,)
