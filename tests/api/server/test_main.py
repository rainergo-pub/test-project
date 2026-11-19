from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from app.api.server.dependencies import get_config
from app.api.server.main import api
from app.api.settings.configs import Config
from app.project_core.data_structures.enums import Stage


@pytest.fixture
def client() -> Iterator[TestClient]:
    api.dependency_overrides[get_config] = lambda: Config.model_validate({"stage": Stage.PROD})
    with TestClient(api) as test_client:  # "with" also runs the lifespan
        yield test_client
    api.dependency_overrides.clear()


def test_health_answers_ok(client: TestClient) -> None:
    response: Response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_stage_returns_the_configured_stage(client: TestClient) -> None:
    response: Response = client.get("/stage")

    assert response.status_code == 200
    assert response.json() == {"stage": "prod"}
