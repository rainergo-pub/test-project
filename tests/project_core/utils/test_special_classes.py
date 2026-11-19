from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from app.project_core.utils.special_classes import DotDict


@pytest.fixture
def toml_file(tmp_path: Path) -> Path:
    path: Path = tmp_path / "params.toml"
    path.write_text(
        'name = "x"\nratio = 0.5\n[section]\nnumbers = [1, 2]\n[section.sub]\ncount = 3\n[[items_list]]\nid = 1\n'
    )
    return path


def test_tables_become_dotdicts_with_attribute_access(toml_file: Path) -> None:
    params: DotDict = DotDict.from_toml(path=toml_file)

    assert isinstance(params, DotDict)
    assert isinstance(params.section, dict)
    assert params.section.sub.count == 3


def test_other_toml_types_are_unchanged(toml_file: Path) -> None:
    params: DotDict = DotDict.from_toml(path=toml_file)

    assert params.name == "x"
    assert params.ratio == 0.5
    assert params.section.numbers == [1, 2]
    assert type(params.section.numbers) is list


def test_tables_inside_arrays_become_dotdicts(toml_file: Path) -> None:
    assert DotDict.from_toml(path=toml_file).items_list[0].id == 1


def test_rejects_keys_that_clash_with_dict_attributes(tmp_path: Path) -> None:
    path: Path = tmp_path / "bad.toml"
    path.write_text("[section]\nitems = 1\n")

    with pytest.raises(ValueError, match="items"):
        DotDict.from_toml(path=path)


def test_attribute_set_and_delete_change_the_dict() -> None:
    params: DotDict = DotDict()

    params.key = 1
    assert params == {"key": 1}

    del params.key
    assert params == {}


def test_setting_a_dict_attribute_name_is_refused() -> None:
    with pytest.raises(AttributeError, match="items"):
        DotDict().items = 1  # ty: ignore[invalid-assignment] - the wrong assignment is what is tested


def test_missing_key_raises_attribute_error() -> None:
    with pytest.raises(AttributeError, match="missing"):
        _: object = DotDict().missing


class _ModelWithDotDict(BaseModel):
    data: DotDict


def test_pydantic_validates_plain_dict_into_nested_dotdicts() -> None:
    model: _ModelWithDotDict = _ModelWithDotDict(data={"section": {"count": 3}})

    assert isinstance(model.data.section, DotDict)
    assert model.data.section.count == 3


def test_pydantic_rejects_non_dict_input_for_dotdict() -> None:
    with pytest.raises(ValidationError, match="dict"):
        _ModelWithDotDict.model_validate({"data": [1, 2]})
