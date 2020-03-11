from features.enums import FeatureTagSource
from features.importers.base import TagMapper
from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Feature, Tag

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


def test_tags_are_imported_based_on_whitelisting(
    requests_mock, importer, places_response
):
    requests_mock.get(PLACES_URL, json=places_response)
    tag_config = {"whitelist": ["Island"]}
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="matko2:47")
    assert tag.name == "Island"


def test_tags_are_imported_based_on_mapping_rules(
    requests_mock, importer, places_response
):
    """Importing tags from external source into internal tags."""
    requests_mock.get(PLACES_URL, json=places_response)
    tag_config = {
        "rules": [
            {"mapped_names": ["Island"], "id": "ahti:tag:island", "name": "saaristo"}
        ],
    }
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="ahti:tag:island")
    assert tag.name == "saaristo"


def test_tags_are_linked_to_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)
    tag_config = {"rules": [], "whitelist": ["Island"]}
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="matko2:47")
    feature = Feature.objects.get(source_id="2792")

    assert feature.tags.count() == 1
    assert tag in feature.tags.all()
    assert feature.feature_tags.first().source == FeatureTagSource.MAPPING
