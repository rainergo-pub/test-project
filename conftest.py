"""Pytest setup for the whole project: tests run in an empty working directory, without local env files or env vars."""

import ast
import os
import shutil
from pathlib import Path

import pytest


def _config_env_vars(*, root: Path) -> set[str]:
    """Return the lower-case env var names that the settings classes in the project's configs.py files read."""
    names: set[str] = set()
    for path in root.rglob("settings/configs.py"):
        if {".venv", "OLD", "experiments"} & set(path.parts):
            continue
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if not isinstance(node, ast.ClassDef):
                continue
            prefix: str = next(
                (
                    str(keyword.value.value)
                    for item in node.body
                    if isinstance(item, ast.Assign) and isinstance(item.value, ast.Call)
                    for keyword in item.value.keywords
                    if keyword.arg == "env_prefix" and isinstance(keyword.value, ast.Constant)
                ),
                "",
            )
            names |= {
                f"{prefix}{item.target.id}".lower()
                for item in node.body
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
            }
    return names


def _empty_dir(*, config: pytest.Config) -> Path:
    """Return the empty working folder of this pytest process; one per process, so nested pytest runs can't clash."""
    return config.rootpath / ".pytest_cache" / f"cwd-{os.getpid()}"


def pytest_configure(config: pytest.Config) -> None:  # noqa: PLR0917 - pytest calls its hooks positionally
    """Before the tests import the settings, remove the settings' env vars and switch to an empty folder."""
    names: set[str] = _config_env_vars(root=config.rootpath)
    for key in [key for key in os.environ if key.lower() in names]:
        del os.environ[key]
    empty_dir: Path = _empty_dir(config=config)
    shutil.rmtree(empty_dir, ignore_errors=True)
    empty_dir.mkdir(parents=True)
    os.chdir(empty_dir)


def pytest_unconfigure(config: pytest.Config) -> None:  # noqa: PLR0917 - pytest calls its hooks positionally
    """Return to the folder pytest was started in and delete the empty folder."""
    os.chdir(config.invocation_params.dir)
    shutil.rmtree(_empty_dir(config=config), ignore_errors=True)
