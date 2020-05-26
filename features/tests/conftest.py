import pytest
from graphene.test import Client

from ahti.schema import schema


@pytest.fixture
def api_client():
    return Client(schema=schema)


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass
