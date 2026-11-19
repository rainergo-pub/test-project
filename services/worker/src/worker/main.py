"""Entry point of worker."""

import logging

from project_core.settings.log_configs import setup_logging
from worker.settings.configs import config
from worker.settings.dir_or_file_paths import dir_or_file_path

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """Configure logging, then run the service."""
    setup_logging(config=config, log_file=dir_or_file_path.log_file)
    logger.info("Here goes the MAIN logic of worker.")


if __name__ == "__main__":
    main()
