from features.importers.venepaikka_harbors.importer import VenepaikkaHarborsClient
from features.models import ContactInfo, Feature
from features.tests.factories import ContactInfoFactory

HARBORS_URL = VenepaikkaHarborsClient.url
HARBOR_ID = "SGFyYm9yTm9kZTpiNzE0ODE1NC1kYmE5LTRlM2ItOWQ2ZS1jNTYzNmEyNWFhMzk="


def test_contact_information_is_imported(requests_mock, importer, harbors_response):
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    feature = Feature.objects.get(source_id=HARBOR_ID)

    contact_info = feature.contact_info
    assert contact_info.street_address == "Ramsaynranta 4"
    assert contact_info.postal_code == "00330"
    assert contact_info.municipality == "Helsinki"
    assert contact_info.phone_number == "+358501234567"
    assert contact_info.email == "venepaikkavaraukset@hel.fi"


def test_contact_info_is_deleted(requests_mock, importer, harbors_response):
    """When address data is not provided, existing ContactInfo will get deleted."""
    ContactInfoFactory(
        feature__source_type=importer.get_source_type(), feature__source_id=HARBOR_ID
    )
    empty_fields = [
        "name",
        "streetAddress",
        "zipCode",
        "municipality",
        "phone",
        "email",
    ]
    for harbor in harbors_response["data"]["harbors"]["edges"]:
        for field in empty_fields:
            harbor["node"]["properties"][field] = ""
    requests_mock.post(HARBORS_URL, json=harbors_response)

    importer.import_features()

    assert ContactInfo.objects.count() == 0
