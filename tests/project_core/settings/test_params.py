import pytest
from pydantic import ValidationError

from app.project_core.data_structures.enums import LoggerType
from app.project_core.settings.params import param


def test_logging_toml_defines_a_handler_for_every_logger_type() -> None:
    assert set(param.logging.handlers) == set(LoggerType)


def test_timezone_is_berlin() -> None:
    assert param.timezone.key == "Europe/Berlin"


def test_param_is_frozen() -> None:
    with pytest.raises(ValidationError, match="frozen"):
        param.timezone = None  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested
