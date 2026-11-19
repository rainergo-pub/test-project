"""Helper classes used across the app."""

import tomllib
from pathlib import Path
from typing import Any, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class DotDict(dict[str, Any]):
    """Dictionary whose keys can also be read, set and deleted as attributes (dot notation)."""

    @classmethod
    def __get_pydantic_core_schema__(  # noqa: PLR0917 - pydantic calls it positionally
        cls, source_type: object, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Let pydantic validate a DotDict field from any str-keyed dict, so models need no arbitrary types."""
        return core_schema.no_info_after_validator_function(
            lambda value: cls._convert(value=value), core_schema.dict_schema(keys_schema=core_schema.str_schema())
        )

    @classmethod
    def from_toml(cls, *, path: Path) -> Self:
        """Load a TOML file; tables become DotDicts, all other types stay as they are."""
        with path.open(mode="rb") as f:
            return cls._convert(value=tomllib.load(f))

    @staticmethod
    def _convert(*, value: object) -> Any:  # noqa: ANN401 - values come from TOML, shape unknown to Python
        """Turn TOML tables into DotDicts recursively, rejecting keys that clash with dict attributes."""
        if isinstance(value, dict):
            clashes: list[str] = [key for key in value if hasattr(dict, key)]
            if clashes:
                raise ValueError(f"TOML keys {clashes} clash with dict attributes; rename them")
            return DotDict({key: DotDict._convert(value=item) for key, item in value.items()})
        if isinstance(value, list):
            return [DotDict._convert(value=item) for item in value]
        return value

    def __getattr__(self, key: str) -> Any:  # noqa: ANN401, PLR0917 - TOML values; Python calls it positionally
        """Return the value for ``key``."""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key: str, value: object) -> None:  # noqa: PLR0917 - Python calls it positionally
        """Set ``key`` to ``value``, refusing names that would be shadowed by dict methods."""
        if hasattr(dict, key):
            raise AttributeError(f"{key!r} is a dict attribute; use item access instead")
        self[key] = value

    def __delattr__(self, key: str) -> None:  # noqa: PLR0917 - Python calls it positionally
        """Delete ``key``."""
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key) from None
