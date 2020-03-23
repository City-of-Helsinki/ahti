import pytest
from utils.pytest import pytest_regex

from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import Image, License
from features.tests.factories import ImageFactory

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


@pytest.fixture(autouse=True)
def setup_images(settings):
    settings.MYHELSINKI_PLACES_ALLOWED_IMAGE_LICENSES = [
        "All rights reserved.",
        "MyHelsinki license type A",
    ]


def test_images_are_imported_for_features(requests_mock, importer, places_response):
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    isosaari_images = Image.objects.filter(feature__source_id="2792")
    assert isosaari_images.count() == 1
    assert isosaari_images.first().url == pytest_regex(r"^https://.*Isosaari.*\.jpg")
    assert Image.objects.filter(feature__source_id="416").count() == 3
    assert Image.objects.count() == 7


def test_updating_images(requests_mock, importer, places_response):
    """Test that image is not re-imported, but rather just updated."""
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


def test_only_import_images_with_allowed_licenses(
    requests_mock, importer, places_response, settings
):
    settings.MYHELSINKI_PLACES_ALLOWED_IMAGE_LICENSES = ["MyHelsinki license type A"]
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    assert (
        Image.objects.filter(
            license__translations__name="All rights reserved.",
        ).count()
        == 0
    )


def test_delete_image_with_wrong_new_license(
    requests_mock, importer, places_response, settings
):
    # Reduce the set of allowed image licenses
    settings.MYHELSINKI_PLACES_ALLOWED_IMAGE_LICENSES = ["MyHelsinki license type A"]
    ImageFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id="2792",
        license__name="All rights reserved.",
    )
    requests_mock.get(PLACES_URL, json=places_response)

    importer.import_features()

    assert (
        Image.objects.filter(
            feature__source_id="2792",
            license__translations__name="All rights reserved.",
        ).count()
        == 0
    )


def test_image_is_deleted(requests_mock, importer, places_response):
    """When a specific image is not available any more it should be deleted.

    Most likely it means that the image not available on the previous url.
    """
    ImageFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id="2792",
        license__name="All rights reserved.",
    )
    requests_mock.get(PLACES_URL, json=places_response)

    # Remove all images from the response
    for place in places_response["data"]:
        place["description"]["images"] = []

    importer.import_features()

    assert Image.objects.count() == 0
