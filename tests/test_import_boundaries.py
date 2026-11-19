import ast
from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _subpackages(*, root: Path) -> list[str]:
    """Return the names of the subpackages of app/: project_core and the services."""
    return sorted(path.parent.name for path in (root / "app").glob("*/__init__.py"))


def _imported_subpackages(*, root: Path, paths: list[Path]) -> set[str]:
    """Return the names below app that the Python files import, such as a service's, archived code excepted."""
    names: set[str] = set()
    for path in paths:
        if "OLD" in path.parts:
            continue
        package: list[str] = list(path.relative_to(root).parent.parts)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules: list[list[str]] = []
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".") for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base: list[str] = package[: len(package) - node.level + 1] if node.level else []
                module: list[str] = base + (node.module.split(".") if node.module else [])
                # from app import <service>: the imported names are the subpackages
                modules = [[*module, alias.name] for alias in node.names] if module == ["app"] else [module]
            names |= {module[1] for module in modules if len(module) > 1 and module[0] == "app"}
    return names


def _violations(*, root: Path) -> dict[str, set[str]]:
    """Return, per subpackage, what it imports from app beyond what its image contains: itself and project_core."""
    found: dict[str, set[str]] = {
        name: _imported_subpackages(root=root, paths=list((root / "app" / name).rglob("*.py"))) - {name, "project_core"}
        for name in _subpackages(root=root)
    }
    # the files directly in app/, such as app/__init__.py, are in every image, so they import nothing from app
    found["app"] = _imported_subpackages(root=root, paths=list((root / "app").glob("*.py")))
    return {name: imported for name, imported in found.items() if imported}


def test_project_core_and_services_import_only_what_their_image_contains(project_root: Path) -> None:
    subpackages: list[str] = _subpackages(root=project_root)
    assert "project_core" in subpackages
    assert set(subpackages) - {"project_core"}
    assert _violations(root=project_root) == {}


def test_finds_a_service_imported_by_project_core_or_another_service(tmp_path: Path) -> None:
    for module, code in [
        ("app/__init__.py", ""),
        ("app/project_core/__init__.py", "from app.scraper.main import main\n"),
        ("app/scraper/__init__.py", "from app.project_core import settings\n"),
        ("app/features/__init__.py", "from app import scraper\n"),
        ("app/features/steps/run.py", "from ...scraper.main import main\n"),
        ("app/reports/__init__.py", "import app.features.steps\n"),
    ]:
        path: Path = tmp_path / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")

    assert _violations(root=tmp_path) == {
        "project_core": {"scraper"},
        "features": {"scraper"},
        "reports": {"features"},
    }


def test_finds_imports_of_code_in_app_that_no_image_contains(tmp_path: Path) -> None:
    for module, code in [
        ("app/__init__.py", "from app import scraper\n"),
        ("app/common.py", ""),
        ("app/project_core/__init__.py", "import app.common\n"),
        ("app/scraper/__init__.py", "from app.shared.helpers import clean\nfrom app import common\n"),
    ]:
        path: Path = tmp_path / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")

    assert _violations(root=tmp_path) == {
        "app": {"scraper"},
        "project_core": {"common"},
        "scraper": {"shared", "common"},
    }


def test_relative_import_inside_a_service_is_no_violation(tmp_path: Path) -> None:
    for module, code in [
        ("app/__init__.py", ""),
        ("app/project_core/__init__.py", ""),
        ("app/scraper/__init__.py", "from .settings import configs\nfrom ..project_core import utils\n"),
    ]:
        path: Path = tmp_path / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")

    assert _violations(root=tmp_path) == {}
