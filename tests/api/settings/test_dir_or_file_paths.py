import pytest
from pydantic import ValidationError

from app.api.settings.dir_or_file_paths import dir_or_file_path


def test_paths_are_frozen() -> None:
    with pytest.raises(ValidationError, match="frozen"):
        dir_or_file_path.log_file = dir_or_file_path.env_files  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested


def test_log_file_lies_in_logs_dir() -> None:
    assert dir_or_file_path.log_file.parent == dir_or_file_path.logs_dir


def test_own_env_file_is_read_last() -> None:
    assert dir_or_file_path.env_files[-1].name == "api.env"
    assert all(path.parent == dir_or_file_path.env_files_dir for path in dir_or_file_path.env_files)


def test_data_dir_resolves_against_the_working_directory() -> None:
    assert not dir_or_file_path.data_dir.is_absolute()


def test_param_files_ship_inside_the_package() -> None:
    assert dir_or_file_path.param_files_dir.is_relative_to(dir_or_file_path.service_dir)
