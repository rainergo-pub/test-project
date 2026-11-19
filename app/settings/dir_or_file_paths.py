"""Central registry of filesystem locations."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DirOrFilePath(BaseModel):
    """Filesystem locations; every directory attribute must end in ``_dir``."""

    model_config = ConfigDict(frozen=True)

    # BASE
    app_dir: Path = Path(__file__).resolve().parents[1]
    settings_dir: Path = app_dir / "settings"
    data_structures_dir: Path = app_dir / "data_structures"
    param_files_dir: Path = settings_dir / "param_files"
    example_toml: Path = param_files_dir / "example.toml"
    logging_toml: Path = param_files_dir / "logging.toml"

    # ENV and LOGS
    env_files: tuple[Path, ...] = (Path(".env"),)  # read in this order; a later file wins
    logs_dir: Path = Path("logs")
    log_file: Path = logs_dir / "app.log"

    # DATA (relative to the working directory; in a container a mounted volume, such as /app/data)
    data_dir: Path = Path("data")


dir_or_file_path: DirOrFilePath = DirOrFilePath()


if __name__ == "__main__":
    print(dir_or_file_path.example_toml)
