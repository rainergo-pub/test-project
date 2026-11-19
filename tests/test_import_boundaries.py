import ast
from pathlib import Path

import pytest


@pytest.fixture
def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _members(*, root: Path, group: str) -> dict[str, Path]:
    """Map the package name of each workspace member in root/group/ to the member's folder."""
    return {
        package.name: package.parents[1]
        for package in sorted((root / group).glob("*/src/*"))
        if (package / "__init__.py").is_file()
    }


def _imported_packages(*, folder: Path) -> set[str]:
    """Return the top-level names of all absolute imports in the Python files below folder, archived code excepted."""
    names: set[str] = set()
    for path in folder.rglob("*.py"):
        if "OLD" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names |= {alias.name.partition(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.partition(".")[0])
    return names


def _violations(*, root: Path) -> dict[str, set[str]]:
    """Return, per member, the services it imports although it must not: libraries none, services no other one."""
    services: dict[str, Path] = _members(root=root, group="services")
    members: dict[str, Path] = {**_members(root=root, group="libs"), **services}
    found: dict[str, set[str]] = {
        name: _imported_packages(folder=folder) & (set(services) - {name}) for name, folder in members.items()
    }
    return {name: imported for name, imported in found.items() if imported}


def test_libraries_and_services_import_no_foreign_service(workspace_root: Path) -> None:
    assert _members(root=workspace_root, group="services")
    assert _members(root=workspace_root, group="libs")
    assert _violations(root=workspace_root) == {}


def test_finds_a_service_imported_by_a_library_or_another_service(tmp_path: Path) -> None:
    for member, code in [
        ("libs/core", "from scraper.main import main\n"),
        ("services/scraper", "import core\n"),
        ("services/features", "import scraper.settings\n"),
    ]:
        package: Path = tmp_path / member / "src" / Path(member).name
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(code, encoding="utf-8")

    assert _violations(root=tmp_path) == {"core": {"scraper"}, "features": {"scraper"}}
