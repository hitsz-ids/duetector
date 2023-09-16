import pytest
from fastapi.testclient import TestClient

from duetector.analyzer.db import DBAnalyzer
from duetector.managers.analyzer import AnalyzerManager
from duetector.service.app import app
from duetector.service.config import get_config


@pytest.fixture
def configed_app(full_config):
    app.dependency_overrides = {get_config: lambda: full_config}
    return app


@pytest.fixture
def db_analyzer(full_config):
    config = AnalyzerManager(full_config).config._config_dict

    yield DBAnalyzer(config)


@pytest.fixture
def client(configed_app):
    with TestClient(configed_app) as client:
        yield client


def test_query(client: TestClient, db_analyzer):
    response = client.get(f"/query/")
    assert response.status_code == 200
    assert "analyzers" in response.json()
    assert db_analyzer.config_scope in response.json()["analyzers"]


def test_query_brief(client: TestClient, db_analyzer):
    response = client.get(f"/query/{db_analyzer.config_scope}/brief")
    assert response.status_code == 200
    assert response.json()


def test_query_analyzer(client: TestClient, db_analyzer):
    response = client.post(f"/query/{db_analyzer.config_scope}")
    assert response.status_code == 200
    assert response.json()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
