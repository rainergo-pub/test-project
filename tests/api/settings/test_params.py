import pytest
from pydantic import ValidationError

from app.api.settings.params import param


def test_param_is_frozen() -> None:
    with pytest.raises(ValidationError, match="frozen"):
        param.any_field = None  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested
