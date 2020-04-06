import math

import pytest

from features.enums import FeatureDetailsType, HarborMooringType
from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import Feature, FeatureDetails
from features.tests.factories import FeatureDetailsFactory

HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


@pytest.fixture(autouse=True)
def setup_mooring_mapping(settings):
    settings.VENEPAIKKA_HARBORS_MOORING_MAPPING = {
        "SINGLE_SLIP_PLACE": "SLIP",
        "SIDE_SLIP_PLACE": "SLIP",
        "STERN_BUOY_PLACE": "STERN_BUOY",
        "QUAYSIDE_MOORING": "QUAYSIDE",
    }


def test_harbor_details_objects_are_created(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    assert FeatureDetails.objects.filter(type=FeatureDetailsType.HARBOR).count() == 2


def test_berth_mooring_types_are_imported(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID)
    details = feature.details.get(type=FeatureDetailsType.HARBOR)
    mooring_types = set(details.data["berth_moorings"])
    assert mooring_types == {HarborMooringType.SLIP, HarborMooringType.STERN_BUOY}


def test_berth_depths_are_imported(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID)
    details = feature.details.get(type=FeatureDetailsType.HARBOR)
    assert math.isclose(details.data["berth_min_depth"], 2)
    assert math.isclose(details.data["berth_max_depth"], 2)


def test_update_harbor_details(requests_mock, importer, harbors_response):
    """Empty data object is not empty after import."""
    details = FeatureDetailsFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id=HARBOR_ID,
        type=FeatureDetailsType.HARBOR,
        data={},
    )
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    details.refresh_from_db()
    assert "berth_moorings" in details.data


def test_delete_harbor_details(requests_mock, importer, harbors_response):
    FeatureDetailsFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id=HARBOR_ID,
        type=FeatureDetailsType.HARBOR,
    )
    requests_mock.post(HARBORS_URL, json=harbors_response)

    # Remove piers and berths from response
    for harbor in harbors_response["data"]["harbors"]["edges"]:
        harbor["node"]["properties"]["piers"] = []

    importer.import_features()

    assert FeatureDetails.objects.filter(type=FeatureDetailsType.HARBOR).count() == 0
