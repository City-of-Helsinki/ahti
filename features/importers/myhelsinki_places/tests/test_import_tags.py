import pytest

from features.enums import FeatureTagSource
from features.importers.base import TagMapper
from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Feature, Tag
from features.tests.factories import FeatureFactory, TagFactory

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url
SOURCE_ID = "2792"  # Source identifier for a feature in the places response


@pytest.fixture(autouse=True)
def setup_tags(settings):
    settings.MYHELSINKI_PLACES_TAG_CONFIG = {
        "rules": [
            {"mapped_names": ["Island"], "id": "ahti:tag:island", "name": "saaristo"}
        ],
    }


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

    importer.import_features()

    tag = Tag.objects.get(id="ahti:tag:island")
    assert tag.name == "saaristo"


def test_tags_are_linked_to_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)
    tag_config = {"rules": [], "whitelist": ["Island"]}
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="matko2:47")
    feature = Feature.objects.get(source_id=SOURCE_ID)

    assert feature.tags.count() == 1
    assert tag in feature.tags.all()
    assert feature.feature_tags.first().source == FeatureTagSource.MAPPING


@pytest.mark.parametrize(
    "tag_id,tag_name",
    [
        # Tag does not appear in the places response
        ("tagyoureit", "tag"),
        # Tag appears in the response and is also configured to be imported
        ("ahti:tag:island", "saaristo"),
    ],
)
def test_manually_set_tags_are_not_touched_when_importing(
    tag_id, tag_name, requests_mock, importer, places_response, settings
):
    """Tags which are manually set for a feature should not be modified by the importer.

    Parametrized tag is assigned to a feature which will be updated by the importer.

    Given one imported tag and one different manual tag (test parameters),
    the expectation after importing is that both manually set tags are still considered
    manually set for the given feature.

    Only FeatureTag objects with source as MAPPING are automatically managed.
    FeatureTag.source should not be changed from MANUAL to MAPPING.
    """
    requests_mock.get(PLACES_URL, json=places_response)
    expected_tag_ids = {
        rule["id"] for rule in settings.MYHELSINKI_PLACES_TAG_CONFIG["rules"]
    }
    expected_tag_ids.add(tag_id)
    tag = TagFactory(id=tag_id, name=tag_name)
    feature = FeatureFactory(
        source_type=importer.get_source_type(), source_id=SOURCE_ID
    )
    feature.tags.add(tag, through_defaults={"source": FeatureTagSource.MANUAL})

    importer.import_features()

    assert feature.feature_tags.count() == len(expected_tag_ids)
    assert feature.feature_tags.get(tag_id=tag_id).source == FeatureTagSource.MANUAL
