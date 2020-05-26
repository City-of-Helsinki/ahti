import pytest
from utils.utils import read_json_file

from features.importers.myhelsinki_places.importer import MyHelsinkiImporter


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def setup_test_environment(settings):
    settings.MYHELSINKI_PLACES_API_CALLS = [
        {}
    ]  # Response is mocked, parameters are redundant

    # Only import Finnish on tests by default
    settings.MYHELSINKI_PLACES_ADDITIONAL_LANGUAGES = []


@pytest.fixture
def importer():
    return MyHelsinkiImporter()


@pytest.fixture
def places_response():
    return read_json_file(__file__, "responses", "places_response.json")


@pytest.fixture
def translations_responses():
    return {
        "en": read_json_file(__file__, "responses", "places_en.json"),
        "sv": read_json_file(__file__, "responses", "places_sv.json"),
    }
