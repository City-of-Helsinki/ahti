import pytest

from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Feature
from utils.pytest import pytest_regex

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


@pytest.fixture(autouse=True)
def setup_test_translations(settings):
    settings.MYHELSINKI_PLACES_ADDITIONAL_LANGUAGES = ["en", "sv"]


def test_feature_translations_are_imported(
    requests_mock, importer, places_response, translations_responses
):
    requests_mock.get(f"{PLACES_URL}?language_filter=fi", json=places_response)
    requests_mock.get(
        f"{PLACES_URL}?language_filter=en", json=translations_responses["en"]
    )
    requests_mock.get(
        f"{PLACES_URL}?language_filter=sv", json=translations_responses["sv"]
    )

    importer.import_features()

    feature = Feature.objects.get(source_id="416")  # Suomenlinna
    ohp = feature.opening_hours_periods.first()

    assert feature.translations.all().count() == 3
    assert ohp.translations.all().count() == 3

    feature.set_current_language("fi")
    ohp.set_current_language("fi")
    assert feature.name == "Suomenlinnan merilinnoitus"
    assert feature.description == pytest_regex(
        "^Suomenlinnan merilinnoitus on upea Unescon.*"
    )
    assert feature.url == "http://www.suomenlinna.fi"
    assert ohp.comment == pytest_regex("^Suomenlinna on.*")

    feature.set_current_language("en")
    ohp.set_current_language("en")
    assert feature.name == "Suomenlinna Sea Fortress"
    assert feature.description == pytest_regex("^A Unesco World Heritage Site.*")
    assert feature.url == "http://www.suomenlinna.fi"
    assert ohp.comment == pytest_regex("^Suomenlinna island.*")

    feature.set_current_language("sv")
    ohp.set_current_language("sv")
    assert feature.name == "Sveaborgs sjöfästning"
    assert feature.description == pytest_regex("^Sveaborg är ett magnifikt Unescos.*")
    assert feature.url == "http://www.suomenlinna.fi"
    assert ohp.comment == pytest_regex("^Sveaborg är.*")
