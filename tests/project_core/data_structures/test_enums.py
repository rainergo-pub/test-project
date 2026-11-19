import logging

import pytest

from app.project_core.data_structures.enums import LogLevel


@pytest.mark.parametrize("level", list(LogLevel))
def test_log_level_is_accepted_by_logging(level: LogLevel) -> None:
    assert level in logging.getLevelNamesMapping()
