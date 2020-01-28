from utils.pytest import pytest_regex

from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Image, License

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


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
