import pytest

from categories.models import Category
from categories.tests.factories import CategoryFactory
from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import Feature
from features.tests.factories import FeatureFactory


@pytest.fixture(autouse=True)
def setup_categories(settings):
    settings.VENEPAIKKA_HARBORS_CATEGORY_CONFIG = {
        "id": "ahti:category:harbor",
        "name": "Satamat",
    }


HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


def test_import_feature_category(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    f = Feature.objects.get(source_id=HARBOR_ID)
    assert Category.objects.count() == 1
    assert f.categories.first().id == "ahti:category:harbor"
    assert f.categories.first().name == "Satamat"
    assert f.categories.first().description == ""


def test_feature_category_is_not_updated(requests_mock, importer, harbors_response):
    """If a feature already has a category, import must not change it."""
    requests_mock.post(HARBORS_URL, json=harbors_response)
    category = CategoryFactory()
    f = FeatureFactory(source_type=importer.get_source_type(), source_id=HARBOR_ID,)
    f.categories.add(category)

    orig_updated = f.modified_at

    importer.import_features()

    f.refresh_from_db()
    assert f.modified_at > orig_updated  # Model gets touched by the importer
    assert f.categories.filter(id=category.id)
