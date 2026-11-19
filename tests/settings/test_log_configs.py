import json
import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.data_structures.enums import LoggerType, LogLevel
from app.settings import log_configs
from app.settings.configs import Config
from app.settings.dir_or_file_paths import dir_or_file_path
from app.settings.log_configs import JsonFormatter, setup_logging
from app.settings.params import param
from app.utils.special_classes import DotDict


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
    return logging.LogRecord("app.test", logging.ERROR, "module.py", 7, message, None, exc_info)


def _json_formatter() -> JsonFormatter:
    return JsonFormatter(fields=param.logging.formatters.json.fields)


def _use_config(*, monkeypatch: pytest.MonkeyPatch, **values: object) -> None:
    monkeypatch.setattr(log_configs, "config", Config.model_validate(values))


def test_sets_root_level_and_handlers_from_config(monkeypatch: pytest.MonkeyPatch) -> None:
    _use_config(monkeypatch=monkeypatch, log_level=LogLevel.DEBUG, log_handlers=(LoggerType.CONSOLE, LoggerType.JSON))

    setup_logging()

    root: logging.Logger = logging.getLogger()
    assert root.level == logging.DEBUG
    assert {handler.name for handler in root.handlers} == {"console", "json"}


def test_file_handler_creates_log_file_in_working_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _use_config(monkeypatch=monkeypatch, log_handlers=(LoggerType.FILE,))

    setup_logging()
    logging.getLogger("app.test").warning("written to file")

    assert "written to file" in (tmp_path / dir_or_file_path.log_file).read_text()


def test_does_not_create_log_dir_without_file_handler(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _use_config(monkeypatch=monkeypatch, log_handlers=(LoggerType.CONSOLE,))

    setup_logging()

    assert not (tmp_path / dir_or_file_path.logs_dir).exists()


def test_json_handler_writes_to_stdout(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _use_config(monkeypatch=monkeypatch, log_handlers=(LoggerType.JSON,))

    setup_logging()
    logging.getLogger("app.test").warning("to stdout")

    out, err = capsys.readouterr()
    assert json.loads(out)["message"] == "to stdout"
    assert err == ""


def test_does_not_modify_logging_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _use_config(monkeypatch=monkeypatch, log_handlers=tuple(LoggerType))

    setup_logging()

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
