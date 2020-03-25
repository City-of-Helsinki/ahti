import datetime
import math

from django.contrib.gis.geos import Point
from django.utils.timezone import utc
from freezegun import freeze_time

from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import Feature, SourceType
from features.tests.factories import LinkFactory

HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


def test_import_all_harbors_from_source(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    assert Feature.objects.count() == 2


def test_source_type_gets_created(requests_mock, importer):
    empty_response = {"data": {"harbors": {"edges": []}}}
    requests_mock.post(HARBORS_URL, json=empty_response)

    importer.import_features()

    assert SourceType.objects.count() == 1
    assert SourceType.objects.filter(system="venepaikka", type="harbor").exists()


@freeze_time("2019-12-16 12:00:01")
def test_data_for_feature_is_correct(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    source_type = SourceType.objects.first()
    feature = Feature.objects.get(source_type=source_type, source_id=HARBOR_ID)
    assert feature.name == "Ramsaynrannan venesatama (Ramsaynranta 4)"
    assert feature.description == ""
    assert feature.source_modified_at == datetime.datetime(
        2019, 12, 16, 12, 0, 1
    ).replace(tzinfo=utc)
    assert feature.mapped_at == datetime.datetime(2019, 12, 16, 12, 0, 1).replace(
        tzinfo=utc
    )


def test_service_map_url_is_imported(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID)
    link = feature.links.first()
    assert link.type == "servicemap"
    assert link.url == "https://palvelukartta.hel.fi/fi/unit/41074"


def test_service_map_url_is_deleted(requests_mock, importer, harbors_response):
    """Service map link is removed from a feature if response doesn't contain id."""
    LinkFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id=HARBOR_ID,
        type="servicemap",
    )
    for harbor in harbors_response["data"]["harbors"]["edges"]:
        harbor["node"]["properties"]["servicemapId"] = None
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID)
    link = feature.links.first()
    assert link is None


def test_geometry_is_correct(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID,)
    assert isinstance(feature.geometry, Point)
    assert math.isclose(feature.geometry.x, 24.884083)
    assert math.isclose(feature.geometry.y, 60.193653)
