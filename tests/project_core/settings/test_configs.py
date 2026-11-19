from pathlib import Path

import pytest
from pydantic import ValidationError

from app.project_core.data_structures.enums import LoggerType, LogLevel, Stage
from app.project_core.settings.configs import ProjectConfig


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run each test in an empty working directory without any of the project's env vars set."""
    monkeypatch.chdir(tmp_path)
    for name in ProjectConfig.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    return tmp_path


def test_defaults_without_env_vars() -> None:
    config: ProjectConfig = ProjectConfig()

    assert config.stage is Stage.DEV
    assert config.log_level is LogLevel.INFO
    assert config.log_handlers == (LoggerType.CONSOLE,)


def test_reads_no_env_file_of_its_own(isolated_env: Path) -> None:
    (isolated_env / ".env").write_text("LOG_LEVEL=DEBUG\n")

    assert ProjectConfig().log_level is LogLevel.INFO


def test_empty_env_var_counts_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "")

    assert ProjectConfig().log_level is LogLevel.INFO


def test_log_handlers_parsed_from_json_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_HANDLERS", '["console", "file"]')

    assert ProjectConfig().log_handlers == (LoggerType.CONSOLE, LoggerType.FILE)


def test_rejects_unknown_log_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_HANDLERS", '["sms"]')

    with pytest.raises(ValidationError, match="log_handlers"):
        ProjectConfig()


def test_config_is_frozen() -> None:
    config: ProjectConfig = ProjectConfig()

    with pytest.raises(ValidationError, match="frozen"):
        config.log_level = LogLevel.DEBUG  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested
