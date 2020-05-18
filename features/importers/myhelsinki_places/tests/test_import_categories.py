import pytest

from categories.models import Category
from categories.tests.factories import CategoryFactory
from features.importers.myhelsinki_places.importer import (
    MyHelsinkiImporter,
    MyHelsinkiPlacesClient,
)
from features.models import Feature
from features.tests.factories import FeatureFactory

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


@pytest.fixture(autouse=True)
def setup_categories(settings):
    settings.MYHELSINKI_PLACES_CATEGORY_CONFIG = {
        "rules": [
            {
                "mapped_names": ["Island"],
                "id": "ahti:category:island",
                "name": "Saaret",
            },
            {"mapped_names": ["Golf"], "id": "ahti:category:golf", "name": "Golf"},
        ],
    }


def test_import_feature_category(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)
    importer.import_features()

    f = Feature.objects.get(source_id=2792)
    Category.objects.filter(id="ahti:category:island").update(principle=True)
    assert Category.objects.count() == 2
    assert f.categories.first().pk == "ahti:category:island"
    assert f.categories.first().name == "Saaret"
    assert f.categories.first().description == ""
    assert f.categories.last().pk == "ahti:category:golf"
    assert f.categories.last().name == "Golf"
    assert f.categories.last().description == ""


def test_category_is_not_set_when_no_mapping_matches(
    requests_mock, places_response, settings
):
    requests_mock.get(PLACES_URL, json=places_response)
    settings.MYHELSINKI_PLACES_CATEGORY_CONFIG = {
        "rules": [{"mapped_names": ["nope"], "id": "nope", "name": "Nope"}],
    }
    importer = MyHelsinkiImporter()

    importer.import_features()

    f = Feature.objects.get(source_id=2792)
    assert not f.categories.all()
    assert Category.objects.count() == 0


def test_feature_category_is_not_updated(requests_mock, importer, places_response):
    """If a feature already has a category, import must not change it.
    However, new ones can be added"""
    requests_mock.get(PLACES_URL, json=places_response)
    category = CategoryFactory()
    f = FeatureFactory(source_type=importer.get_source_type(), source_id="2792",)
    f.categories.add(category)
    orig_updated = f.modified_at

    importer.import_features()

    f.refresh_from_db()
    assert f.modified_at > orig_updated  # Model gets touched by the importer
    assert f.categories.filter(id=category.id)
