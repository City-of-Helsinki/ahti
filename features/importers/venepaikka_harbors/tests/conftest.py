import json
from pathlib import PurePath

import pytest

from features.importers.venepaikka_harbors.importer import VenepaikkaImporter


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def importer():
    return VenepaikkaImporter()


@pytest.fixture
def harbors_response():
    path = PurePath(__file__).parent.joinpath("responses", "harbors_response.json")
    with open(path.as_posix(), "r") as f:
        response = json.loads(f.read())
    return response
