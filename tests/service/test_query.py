import pytest
from fastapi.testclient import TestClient

from duetector.analyzer.db import DBAnalyzer
from duetector.service.app import app
from duetector.service.config import get_config


@pytest.fixture
def configed_app(full_config):
    app.dependency_overrides = {get_config: lambda: full_config}
    return app


@pytest.fixture
def client(configed_app):
    with TestClient(configed_app) as client:
        yield client


def test_query(client: TestClient):
    response = client.get(f"/query/")
    assert response.status_code == 200
    assert response.json() == {"analyzers": [DBAnalyzer.config_scope]}


def test_query_brief(client: TestClient):
    response = client.get(f"/query/{DBAnalyzer.config_scope}/brief")
    assert response.status_code == 200
    assert response.json()


def test_query_analyzer(client: TestClient):
    response = client.post(f"/query/{DBAnalyzer.config_scope}")
    assert response.status_code == 200
    assert response.json()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
