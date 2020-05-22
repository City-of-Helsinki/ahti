import pytest
from utils.utils import read_json_file

from features.importers.venepaikka_harbors.importer import VenepaikkaImporter


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def importer():
    return VenepaikkaImporter()


@pytest.fixture
def harbors_response():
    return read_json_file(__file__, "responses", "harbors_response.json")
