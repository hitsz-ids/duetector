import pytest

from duetector.analyzer.db import DBAnalyzer


@pytest.fixture
def db_analyzer(full_config):
    yield DBAnalyzer(full_config)
