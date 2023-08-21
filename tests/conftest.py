import pytest

CONFIG = """
[]

"""


@pytest.fixture
def config():
    yield {}
