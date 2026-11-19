from pathlib import Path

import pytest
from pydantic import ValidationError

from project_core.data_structures.enums import LogLevel, Stage
from project_core.settings.configs import ProjectConfig
from worker.settings.configs import Config
from worker.settings.dir_or_file_paths import dir_or_file_path


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run each test in an empty working directory without any of the service's env vars set."""
    monkeypatch.chdir(tmp_path)
    for name in Config.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
    return tmp_path


@pytest.fixture
def env_file() -> Path:
    """The last env file read (the service's own), with its folder created in the working directory."""
    path: Path = dir_or_file_path.env_files[-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def test_extends_the_project_config() -> None:
    assert issubclass(Config, ProjectConfig)
    assert Config().log_level is LogLevel.INFO


def test_reads_env_file_from_working_directory(env_file: Path) -> None:
    env_file.write_text("OPENAI_API_KEY=sk-test\nLOG_LEVEL=DEBUG\n")

    config: Config = Config()

    assert config.openai_api_key is not None
    assert config.openai_api_key.get_secret_value() == "sk-test"
    assert config.log_level is LogLevel.DEBUG


def test_env_var_overrides_env_file(env_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file.write_text("STAGE=dev\n")
    monkeypatch.setenv("STAGE", "prod")

    assert Config().stage is Stage.PROD


def test_empty_env_file_value_counts_as_unset(env_file: Path) -> None:
    env_file.write_text("OPENAI_API_KEY=\n")

    assert Config().openai_api_key is None


def test_secret_is_masked_in_repr(env_file: Path) -> None:
    env_file.write_text("OPENAI_API_KEY=sk-secret\n")

    assert "sk-secret" not in repr(Config())


def test_later_env_file_wins(env_file: Path) -> None:
    first: Path = dir_or_file_path.env_files[0]
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text("LOG_LEVEL=WARNING\n")
    with env_file.open(mode="a", encoding="utf-8") as f:
        f.write("LOG_LEVEL=DEBUG\n")

    assert Config().log_level is LogLevel.DEBUG


def test_config_is_frozen() -> None:
    config: Config = Config()

    with pytest.raises(ValidationError, match="frozen"):
        config.log_level = LogLevel.DEBUG  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested
