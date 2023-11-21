import pytest
from fastapi.testclient import TestClient

from duetector.service.app import app
from duetector.service.config import get_config

app.dependency_overrides = {
    get_config: lambda: {
        "server": {
            "token": "test_token",
        }
    }
}


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_root(client: TestClient):
    response = client.get("/", params={"token": "test_token"})
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
