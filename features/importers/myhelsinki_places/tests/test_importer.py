import datetime
from pathlib import PurePath

import pytest
from django.contrib.gis.geos import Point
from django.utils.timezone import utc
from freezegun import freeze_time
from utils.pytest import pytest_regex

from features.importers.base import TagMapper
from features.importers.myhelsinki_places.importer import MyHelsinkiImporter
from features.models import Feature, Image, License, SourceType, Tag

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
    assert f.description == pytest_regex(r".*ulkosaariston helmi Isosaari.*")
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


def test_images_are_imported_for_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    isosaari_images = Image.objects.filter(feature__source_id="2792")
    assert isosaari_images.count() == 1
    assert isosaari_images.first().url == pytest_regex(r"^https://.*Isosaari.*\.jpg")
    assert Image.objects.filter(feature__source_id="416").count() == 3
    assert Image.objects.count() == 4


def test_updating_images(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()
    importer.import_features()

    assert Image.objects.count() == 4


def test_image_licenses_are_imported(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    assert License.objects.count() == 2


def test_image_licenses_is_set_for_an_image(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)

    importer.import_features()

    assert (
        Image.objects.filter(
            feature__source_id="2792",
            license__translations__name="All rights reserved.",
        ).count()
        == 1
    )
    assert (
        Image.objects.filter(
            feature__source_id="416",
            license__translations__name="MyHelsinki license type A",
        ).count()
        == 3
    )


def test_tags_are_imported_based_on_whitelisting(
    requests_mock, importer, places_response
):
    requests_mock.get(PLACES_URL, text=places_response)
    tag_config = {"whitelist": ["Island"]}
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="matko2:47")
    assert tag.name == "Island"


def test_tags_are_imported_based_on_mapping_rules(
    requests_mock, importer, places_response
):
    """Importing tags from external source into internal tags."""
    requests_mock.get(PLACES_URL, text=places_response)
    tag_config = {
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "saaristo"}],
    }
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="ahti:tag:island")
    assert tag.name == "saaristo"


def test_tags_are_linked_to_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, text=places_response)
    tag_config = {"rules": [], "whitelist": ["Island"]}
    importer.tag_mapper = TagMapper(tag_config)

    importer.import_features()

    tag = Tag.objects.get(id="matko2:47")
    feature = Feature.objects.get(source_id="2792")

    assert feature.tags.count() == 1
    assert tag in feature.tags.all()
