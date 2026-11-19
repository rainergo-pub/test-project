"""Entry point of order_worker."""

import logging

from app.order_worker.settings.configs import config
from app.order_worker.settings.dir_or_file_paths import dir_or_file_path
from app.project_core.settings.log_configs import setup_logging

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """Configure logging, then run the service."""
    setup_logging(config=config, log_file=dir_or_file_path.log_file)
    logger.info("Here goes the MAIN logic of order_worker.")


if __name__ == "__main__":
    main()
