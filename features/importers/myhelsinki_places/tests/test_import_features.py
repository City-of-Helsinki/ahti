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


def test_source_type_get_created(requests_mock, importer):
    requests_mock.get(PLACES_URL, json={"data": []})

    importer.import_features()

    assert SourceType.objects.count() == 1
    SourceType.objects.get(system="myhelsinki", type="place")


@freeze_time("2019-12-16 12:00:01")
def test_data_for_feature_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    st = SourceType.objects.first()
    f = Feature.objects.get(source_type=st, source_id="2792")
    assert f.name == "Isosaari"
    assert f.description == pytest_regex(r".*ulkosaariston helmi Isosaari.*")
    assert f.url == "http://www.visitisosaari.fi"
    assert f.source_modified_at == datetime.datetime(2019, 4, 4, 13, 5, 12).replace(
        tzinfo=utc
    )
    assert f.mapped_at == datetime.datetime(2019, 12, 16, 12, 0, 1).replace(tzinfo=utc)


def test_geometry_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    st = SourceType.objects.first()
    f = Feature.objects.get(source_type=st, source_id="2792")
    assert isinstance(f.geometry, Point)
    assert math.isclose(f.geometry.x, 25.052854537963867)
    assert math.isclose(f.geometry.y, 60.10136032104492)
