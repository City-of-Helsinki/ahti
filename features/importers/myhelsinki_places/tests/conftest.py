import json
from pathlib import PurePath

import pytest

from features.importers.myhelsinki_places.importer import MyHelsinkiImporter


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def setup_test_environment(settings):
    settings.MYHELSINKI_PLACES_API_CALLS = [
        {}
    ]  # Response is mocked, parameters are redundant


@pytest.fixture
def importer():
    return MyHelsinkiImporter()


@pytest.fixture
def places_response():
    path = PurePath(__file__).parent.joinpath("responses", "places_response.json")
    with open(path.as_posix(), "r") as f:
        response = json.loads(f.read())
    return response
