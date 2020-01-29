from features.importers.myhelsinki_places.importer import MyHelsinkiPlacesClient
from features.models import ContactInfo, Feature
from features.tests.factories import ContactInfoFactory

PLACES_URL = MyHelsinkiPlacesClient.base_url + MyHelsinkiPlacesClient.places_url


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
