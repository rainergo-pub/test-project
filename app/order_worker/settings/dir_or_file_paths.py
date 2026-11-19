"""Central registry of the filesystem locations of order_worker."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DirOrFilePath(BaseModel):
    """Filesystem locations; every directory attribute must end in ``_dir``."""

    model_config = ConfigDict(frozen=True)

    # BASE
    service_dir: Path = Path(__file__).resolve().parents[1]
    settings_dir: Path = service_dir / "settings"
    data_structures_dir: Path = service_dir / "data_structures"
    param_files_dir: Path = settings_dir / "param_files"

    # ENV and LOGS
    env_files_dir: Path = Path("env_files")
    env_files: tuple[Path, ...] = (  # read in this order; a later file wins
        env_files_dir / "project.env",
        env_files_dir / "order_worker.env",
    )
    logs_dir: Path = Path("logs")
    log_file: Path = logs_dir / "order_worker.log"

    # DATA (relative to the working directory; in a container a mounted volume, such as /app/data)
    data_dir: Path = Path("data")


dir_or_file_path: DirOrFilePath = DirOrFilePath()


if __name__ == "__main__":
    print(dir_or_file_path)
