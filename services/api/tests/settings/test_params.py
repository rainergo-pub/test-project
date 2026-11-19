import pytest
from pydantic import ValidationError

from api.settings.params import param


def test_example_toml_is_loaded() -> None:
    assert param.example.section.param_4 == [1, 2, 3, 4]


def test_param_is_frozen() -> None:
    with pytest.raises(ValidationError, match="frozen"):
        param.any_field = None  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested
