import datetime
import math

from django.contrib.gis.geos import Point
from django.utils.timezone import utc
from freezegun import freeze_time
from utils.pytest import pytest_regex

from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Feature, SourceType

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


def test_import_all_features_from_source(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    assert Feature.objects.count() == 3


def test_source_type_gets_created(requests_mock, importer):
    requests_mock.get(PLACES_URL, json={"data": []})

    importer.import_features()

    assert SourceType.objects.count() == 1
    assert SourceType.objects.filter(system="myhelsinki", type="place").exists()


@freeze_time("2019-12-16 12:00:01")
def test_data_for_feature_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    source_type = SourceType.objects.first()
    feature = Feature.objects.get(source_type=source_type, source_id="2792")
    assert feature.name == "Isosaari"
    assert feature.description == pytest_regex(r".*ulkosaariston helmi Isosaari.*")
    assert feature.url == "http://www.visitisosaari.fi"
    assert feature.source_modified_at == datetime.datetime(
        2019, 4, 4, 13, 5, 12
    ).replace(tzinfo=utc)
    assert feature.mapped_at == datetime.datetime(2019, 12, 16, 12, 0, 1).replace(
        tzinfo=utc
    )


def test_geometry_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    feature = Feature.objects.get(source_id="2792")
    assert isinstance(feature.geometry, Point)
    assert math.isclose(feature.geometry.x, 25.052854537963867)
    assert math.isclose(feature.geometry.y, 60.10136032104492)
