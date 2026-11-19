"""Entry point of api."""

import logging

from api.settings.configs import config
from api.settings.dir_or_file_paths import dir_or_file_path
from project_core.settings.log_configs import setup_logging

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """Configure logging, then run the service."""
    setup_logging(config=config, log_file=dir_or_file_path.log_file)
    logger.info("Here goes the MAIN logic of api.")


if __name__ == "__main__":
    main()
