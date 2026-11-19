"""Entry point of the app."""

import logging

from app.settings.log_configs import setup_logging

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """Configure logging, then run the app."""
    setup_logging()
    logger.info("Here goes the MAIN logic of the app.")


if __name__ == "__main__":
    main()
