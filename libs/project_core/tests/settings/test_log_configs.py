import json
import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from project_core.data_structures.enums import LoggerType, LogLevel
from project_core.settings.configs import ProjectConfig
from project_core.settings.dir_or_file_paths import dir_or_file_path
from project_core.settings.log_configs import JsonFormatter, setup_logging
from project_core.settings.params import param
from project_core.utils.special_classes import DotDict


@pytest.fixture(autouse=True)
def restore_root_logger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Run in an empty working directory and undo setup_logging() after each test."""
    monkeypatch.chdir(tmp_path)
    root: logging.Logger = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    for handler in root.handlers:
        if handler not in handlers:
            handler.close()
    root.handlers[:] = handlers
    root.setLevel(level)


def _record(*, message: str, with_exception: bool = False) -> logging.LogRecord:
    error: ZeroDivisionError = ZeroDivisionError("boom")
    exc_info: tuple[type[BaseException], BaseException, None] | None = (
        (type(error), error, None) if with_exception else None
    )
    return logging.LogRecord("project_core.test", logging.ERROR, "module.py", 7, message, None, exc_info)


def _json_formatter() -> JsonFormatter:
    return JsonFormatter(fields=param.logging.formatters.json.fields)


def _setup(**values: object) -> None:
    setup_logging(config=ProjectConfig.model_validate(values), log_file=Path("logs") / "service.log")


def test_sets_root_level_and_handlers_from_config() -> None:
    _setup(log_level=LogLevel.DEBUG, log_handlers=(LoggerType.CONSOLE, LoggerType.JSON))

    root: logging.Logger = logging.getLogger()
    assert root.level == logging.DEBUG
    assert {handler.name for handler in root.handlers} == {"console", "json"}


def test_file_handler_creates_log_file_in_working_directory(tmp_path: Path) -> None:
    _setup(log_handlers=(LoggerType.FILE,))
    logging.getLogger("project_core.test").warning("written to file")

    assert "written to file" in (tmp_path / "logs" / "service.log").read_text()


def test_does_not_create_log_dir_without_file_handler(tmp_path: Path) -> None:
    _setup(log_handlers=(LoggerType.CONSOLE,))

    assert not (tmp_path / "logs").exists()


def test_json_handler_writes_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    _setup(log_handlers=(LoggerType.JSON,))
    logging.getLogger("project_core.test").warning("to stdout")

    out, err = capsys.readouterr()
    assert json.loads(out)["message"] == "to stdout"
    assert err == ""


def test_does_not_modify_logging_params() -> None:
    _setup(log_handlers=tuple(LoggerType))

    assert param.logging == DotDict.from_toml(path=dir_or_file_path.logging_toml)


def test_json_formatter_escapes_quotes_and_newlines() -> None:
    entry: dict[str, object] = json.loads(_json_formatter().format(_record(message='say "hi"\nnext line')))

    assert entry["message"] == 'say "hi"\nnext line'
    assert entry["level"] == "ERROR"
    assert entry["file"] == "module.py"
    assert entry["line"] == 7
    assert "exception" not in entry


def test_json_formatter_includes_traceback() -> None:
    entry: dict[str, object] = json.loads(_json_formatter().format(_record(message="failed", with_exception=True)))

    assert "ZeroDivisionError: boom" in str(entry["exception"])
