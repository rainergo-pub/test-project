"""Closed sets of enum type values used across the app."""

from enum import StrEnum, auto


class LoggerType(StrEnum):
    """Logging handlers that setup_logging() can attach; values are the handler names in logging.toml."""

    CONSOLE = auto()
    FILE = auto()
    JSON = auto()


class LogLevel(StrEnum):
    """Logging severity threshold; values match the upper case level names of the ``logging`` module."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Stage(StrEnum):
    """Development and deployment stages."""

    DEV = auto()
    PROD = auto()
