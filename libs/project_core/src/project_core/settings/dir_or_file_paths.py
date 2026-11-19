"""Filesystem locations inside the project_core package; each service registers its own env files and logs."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DirOrFilePath(BaseModel):
    """Filesystem locations; every directory attribute must end in ``_dir``."""

    model_config = ConfigDict(frozen=True)

    # BASE
    project_core_dir: Path = Path(__file__).resolve().parents[1]
    settings_dir: Path = project_core_dir / "settings"
    data_structures_dir: Path = project_core_dir / "data_structures"
    param_files_dir: Path = settings_dir / "param_files"
    logging_toml: Path = param_files_dir / "logging.toml"


dir_or_file_path: DirOrFilePath = DirOrFilePath()


if __name__ == "__main__":
    print(dir_or_file_path.logging_toml)
