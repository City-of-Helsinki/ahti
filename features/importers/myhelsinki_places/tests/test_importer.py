import datetime
import json
from pathlib import PurePath

import pytest
from django.contrib.gis.geos import Point
from django.utils.timezone import utc
from freezegun import freeze_time
from utils.pytest import pytest_regex

from features.enums import Weekday
from features.importers.base import TagMapper
from features.importers.myhelsinki_places.importer import MyHelsinkiImporter
from features.models import ContactInfo, Feature, Image, License, SourceType, Tag
from features.tests.factories import ContactInfoFactory, OpeningHoursFactory

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
        response = json.loads(f.read())
    return response


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
    assert f.geometry.x == 25.052854537963867
    assert f.geometry.y == 60.10136032104492


def test_images_are_imported_for_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    isosaari_images = Image.objects.filter(feature__source_id="2792")
    assert isosaari_images.count() == 1
    assert isosaari_images.first().url == pytest_regex(r"^https://.*Isosaari.*\.jpg")
    assert Image.objects.filter(feature__source_id="416").count() == 3
    assert Image.objects.count() == 7


def test_updating_images(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()
    importer.import_features()

    assert Image.objects.count() == 7


def test_image_licenses_are_imported(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    assert License.objects.count() == 2


def test_image_licenses_is_set_for_an_image(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

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
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "saaristo"}],
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


def test_contact_info_is_imported_for_a_feature(
    requests_mock, importer, places_response
):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    f = Feature.objects.get(source_id="2792")
    assert f.contact_info.street_address == "Isosaari"
    assert f.contact_info.postal_code == "00860"
    assert f.contact_info.municipality == "Helsinki"


def test_contact_info_is_deleted(requests_mock, importer, places_response):
    """When address data is not provided, existing ContactInfo will get deleted."""
    ContactInfoFactory(
        feature__source_type=importer.get_source_type(), feature__source_id="2792"
    )
    for place in places_response["data"]:
        place["location"]["address"] = None
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    assert ContactInfo.objects.count() == 0


def test_import_opening_hours(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    f = Feature.objects.get(source_id=364)
    opening_hours = f.opening_hours_periods.first().opening_hours.all()

    # Every day 10 - 17
    for day in Weekday:
        oh = opening_hours.get(day=day)
        assert oh.opens == datetime.time(10)
        assert oh.closes == datetime.time(17)
        assert not oh.all_day


def test_import_opening_hours_period_comments(requests_mock, importer, places_response):
    """Import openinghours_exception as OpeningHoursPeriod.comment"""
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    f = Feature.objects.get(source_id=416)
    assert f.opening_hours_periods.count() == 1
    ohp = f.opening_hours_periods.first()
    assert ohp.comment == pytest_regex("^Suomenlinna on Helsingin kaupunginosa.*")


def test_empty_opening_hours_are_not_imported(requests_mock, importer, places_response):
    """Empty / null opening hours i.e. no opening hours"""
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    # Empty opening hours
    f = Feature.objects.get(source_id=416)
    assert f.opening_hours_periods.count() == 1
    ohp = f.opening_hours_periods.first()
    assert ohp.opening_hours.count() == 0

    # Empty comment, empty opening hours
    f = Feature.objects.get(source_id=2792)
    assert f.opening_hours_periods.count() == 0


def test_update_and_delete_opening_hours(requests_mock, importer, places_response):
    OpeningHoursFactory(
        period__feature__source_type=importer.get_source_type(),
        period__feature__source_id="364",
    )
    for place in places_response["data"]:
        place["opening_hours"]["hours"] = []
        place["opening_hours"]["openinghours_exception"] = ""
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    f = Feature.objects.get(source_id=364)
    assert f.opening_hours_periods.count() == 0


def test_import_open_all_day(requests_mock, importer, places_response):
    for place in places_response["data"]:
        for h in place["opening_hours"]["hours"]:
            h["open24h"] = True
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    f = Feature.objects.get(source_id=364)
    opening_hours = f.opening_hours_periods.first().opening_hours.all()

    for day in Weekday:
        oh = opening_hours.get(day=day)
        assert oh.all_day
