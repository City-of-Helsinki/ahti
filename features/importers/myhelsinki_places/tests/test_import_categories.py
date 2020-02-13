import pytest

from categories.models import Category
from categories.tests.factories import CategoryFactory
from features.importers.base import CategoryMapper
from features.importers.myhelsinki_places.importer import (
    MyHelsinkiImporter,
    MyHelsinkiPlacesClient,
)
from features.models import Feature
from features.tests.factories import FeatureFactory

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


@pytest.fixture(autouse=True)
def setup_images(settings):
    settings.MYHELSINKI_PLACES_CATEGORY_CONFIG = {
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "Saaret"}],
    }


def test_import_feature_category(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)
    category_config = {
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "Saaret"}],
    }
    importer.category_mapper = CategoryMapper(category_config)

    importer.import_features()

    f = Feature.objects.get(source_id=2792)

    assert Category.objects.count() == 1
    assert f.category.pk == "ahti:category:island"
    assert f.category.name == "Saaret"
    assert f.category.description == ""


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

    assert not f.category
    assert Category.objects.count() == 0


def test_feature_category_is_not_updated(requests_mock, importer, places_response):
    """If a feature already has a category, import must not change it."""
    requests_mock.get(PLACES_URL, json=places_response)

    category = CategoryFactory()
    f = FeatureFactory(
        source_type=importer.get_source_type(), source_id="2792", category=category,
    )
    orig_updated = f.modified_at

    importer.import_features()

    f.refresh_from_db()
    assert f.modified_at > orig_updated  # Model gets touched by the importer
    assert f.category.pk == category.pk
