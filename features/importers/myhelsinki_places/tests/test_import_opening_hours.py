import datetime

from features.enums import Weekday
from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Feature
from features.tests.factories import OpeningHoursFactory
from utils.pytest import pytest_regex

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


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
