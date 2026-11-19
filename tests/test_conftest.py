import os
import subprocess
import sys
from pathlib import Path


def test_tests_ignore_the_settings_env_vars_of_the_shell() -> None:
    env: dict[str, str] = {**os.environ, "STAGE": "no-such-stage", "log_handlers": '["no-such-handler"]'}

    result: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
