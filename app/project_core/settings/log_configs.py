"""Logging setup for every service, built from logging.toml, the service's config and its log file."""

import json
import logging
import logging.config
from collections.abc import Mapping
from pathlib import Path

from app.project_core.data_structures.enums import LoggerType
from app.project_core.settings.configs import ProjectConfig
from app.project_core.settings.params import param


class JsonFormatter(logging.Formatter):
    """Format each log record as one JSON object per line, with the fields chosen in ``logging.toml``."""

    def __init__(self, *, fields: Mapping[str, str], datefmt: str | None = None) -> None:
        """Store which LogRecord attribute goes into which JSON key."""
        super().__init__(datefmt=datefmt)
        self.fields: Mapping[str, str] = fields

    def format(self, record: logging.LogRecord) -> str:  # noqa: PLR0917 - overrides logging.Formatter.format
        """Return the record as a JSON string; fields without a value are left out."""
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        entry: dict[str, object] = {
            key: getattr(record, attribute)
            for key, attribute in self.fields.items()
            if getattr(record, attribute) is not None
        }
        return json.dumps(entry, ensure_ascii=False)


def setup_logging(*, config: ProjectConfig, log_file: Path) -> None:
    """Configure the root logger with the handlers and level chosen in the service's config."""
    handlers: dict[LoggerType, dict[str, object]] = {
        name: dict(param.logging.handlers[name]) for name in config.log_handlers
    }
    if LoggerType.FILE in handlers:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers[LoggerType.FILE]["filename"] = log_file
    logging.config.dictConfig(
        {**param.logging, "handlers": handlers, "root": {"handlers": list(handlers), "level": config.log_level}}
    )
