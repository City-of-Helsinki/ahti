import json
from pathlib import PurePath

import pytest

from features.importers.myhelsinki_places.importer import MyHelsinkiImporter


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def importer():
    mhi = MyHelsinkiImporter()
    mhi.api_calls = [{}]  # Response is mocked, parameters are redundant
    return mhi


@pytest.fixture
def places_response():
    path = PurePath(__file__).parent.joinpath("responses", "places_response.json")
    with open(path.as_posix(), "r") as f:
        response = json.loads(f.read())
    return response
