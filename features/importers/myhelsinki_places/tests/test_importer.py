import datetime
from pathlib import PurePath

import pytest
from django.contrib.gis.geos import Point
from django.utils.timezone import utc
from freezegun import freeze_time

from features.importers.myhelsinki_places.importer import MyHelsinkiImporter
from features.models import Feature, SourceType

PLACES_URL = "//open-api.myhelsinki.fi/v1/places/"


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def importer():
    return MyHelsinkiImporter()


@pytest.fixture
def places_response():
    path = PurePath(__file__).parent.joinpath("responses", "places_response.json")
    with open(path.as_posix(), "r") as f:
        response = f.read()
    return response


def test_import_all_features_from_source(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    assert Feature.objects.count() == 2


def test_source_type_get_created(requests_mock, importer):
    requests_mock.get(PLACES_URL, json={"data": []})

    importer.import_features()

    assert SourceType.objects.count() == 1
    SourceType.objects.get(system="myhelsinki", type="place")


@freeze_time("2019-12-16 12:00:01")
def test_data_for_feature_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    st = SourceType.objects.first()
    f = Feature.objects.get(source_type=st, source_id="2792")
    assert f.name == "Isosaari"
    assert f.url == "http://www.visitisosaari.fi"
    assert f.source_modified_at == datetime.datetime(2019, 4, 4, 13, 5, 12).replace(
        tzinfo=utc
    )
    assert f.mapped_at == datetime.datetime(2019, 12, 16, 12, 0, 1).replace(tzinfo=utc)


def test_geometry_is_correct(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    st = SourceType.objects.first()
    f = Feature.objects.get(source_type=st, source_id="2792")
    assert isinstance(f.geometry, Point)
    assert f.geometry.x == 25.052854537963867
    assert f.geometry.y == 60.10136032104492
