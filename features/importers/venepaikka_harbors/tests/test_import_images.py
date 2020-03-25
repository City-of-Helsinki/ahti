import pytest
from utils.pytest import pytest_regex

from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import Image, License
from features.tests.factories import ImageFactory

HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


@pytest.fixture(autouse=True)
def setup_images(settings):
    settings.VENEPAIKKA_HARBORS_IMAGE_LICENSE = "All rights reserved."


def test_image_is_imported(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    images = Image.objects.filter(feature__source_id=HARBOR_ID)
    assert images.count() == 1
    assert images.first().url == pytest_regex(r"^https://.*/harbors/.*\.jpg")


def test_updating_images(requests_mock, importer, harbors_response):
    """Test that image is not re-imported, but rather just updated."""
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()
    importer.import_features()

    assert Image.objects.count() == 2


def test_image_license_is_imported(requests_mock, importer, harbors_response):
    """Image license object gets created when importing."""
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    assert License.objects.count() == 1


def test_image_licenses_is_set_for_an_image(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    assert (
        Image.objects.filter(
            license__translations__name="All rights reserved.",
        ).count()
        == 2
    )


def test_image_is_deleted(requests_mock, importer, harbors_response):
    """When a specific image is not available any more it should be deleted."""
    ImageFactory(
        feature__source_type=importer.get_source_type(),
        feature__source_id=HARBOR_ID,
        license__name="All rights reserved.",
    )
    requests_mock.post(HARBORS_URL, json=harbors_response)

    # Remove all images from the response
    empty_fields = ["imageFile", "imageLink"]
    for harbor in harbors_response["data"]["harbors"]["edges"]:
        for field in empty_fields:
            harbor["node"]["properties"][field] = ""

    importer.import_features()

    assert Image.objects.count() == 0
