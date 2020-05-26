import pytest

from features.enums import FeatureTagSource
from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import Feature, Tag
from features.tests.factories import FeatureFactory, TagFactory


@pytest.fixture(autouse=True)
def setup_tags(settings):
    settings.VENEPAIKKA_HARBORS_TAG_CONFIG = {
        "id": "ahti:tag:harbor",
        "name": "satama",
    }


HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


def test_tags_are_imported_based_on_mapping_rules(
    requests_mock, importer, harbors_response
):
    """Static tag is created when importing."""
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    tag = Tag.objects.get(id="ahti:tag:harbor")
    assert tag.name == "satama"


def test_tag_is_linked_to_features(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    tag = Tag.objects.get(id="ahti:tag:harbor")
    feature = Feature.objects.get(source_id=HARBOR_ID)

    assert feature.tags.count() == 1
    assert tag in feature.tags.all()
    assert feature.feature_tags.first().source == FeatureTagSource.MAPPING


@pytest.mark.parametrize(
    "tag_id,tag_name",
    [
        # Tag does not appear in the places response
        ("tagyoureit", "tag"),
        # Tag is the same which would be automatically assigned
        ("ahti:tag:harbor", "satama"),
    ],
)
def test_manually_set_tags_are_not_touched_when_importing(
    tag_id, tag_name, requests_mock, importer, harbors_response, settings
):
    """Tags which are manually set for a feature should not be modified by the importer.

    Parametrized tag is assigned to a feature which will be updated by the importer.

    Given one imported tag and one different manual tag (test parameters),
    the expectation after importing is that both manually set tags are still considered
    manually set for the given feature.

    Only FeatureTag objects with source as MAPPING are automatically managed.
    FeatureTag.source should not be changed from MANUAL to MAPPING.
    """
    requests_mock.post(HARBORS_URL, json=harbors_response)
    expected_tag_ids = {settings.VENEPAIKKA_HARBORS_TAG_CONFIG["id"]}
    expected_tag_ids.add(tag_id)
    tag = TagFactory(id=tag_id, name=tag_name)
    feature = FeatureFactory(
        source_type=importer.get_source_type(), source_id=HARBOR_ID
    )
    feature.tags.add(tag, through_defaults={"source": FeatureTagSource.MANUAL})

    importer.import_features()

    assert feature.feature_tags.count() == len(expected_tag_ids)
    assert feature.feature_tags.get(tag_id=tag_id).source == FeatureTagSource.MANUAL
