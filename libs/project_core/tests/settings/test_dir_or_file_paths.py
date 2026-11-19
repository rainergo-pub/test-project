import pytest
from pydantic import ValidationError

from project_core.settings.dir_or_file_paths import dir_or_file_path


def test_paths_are_frozen() -> None:
    with pytest.raises(ValidationError, match="frozen"):
        dir_or_file_path.logging_toml = dir_or_file_path.project_core_dir  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested


def test_param_files_ship_inside_the_package() -> None:
    assert dir_or_file_path.logging_toml.is_file()
    assert dir_or_file_path.param_files_dir.is_relative_to(dir_or_file_path.project_core_dir)
