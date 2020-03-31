import pytest

from features.models import (
    ContactInfo,
    Feature,
    Image,
    License,
    Link,
    OpeningHours,
    OpeningHoursPeriod,
    Override,
    SourceType,
    Tag,
)
from features.tests.factories import (
    ContactInfoFactory,
    FeatureFactory,
    ImageFactory,
    LicenseFactory,
    LinkFactory,
    OpeningHoursFactory,
    OpeningHoursPeriodFactory,
    OverrideFactory,
    SourceTypeFactory,
    TagFactory,
)


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_source_type():
    SourceTypeFactory()

    assert SourceType.objects.count() == 1


def test_feature():
    FeatureFactory()

    assert SourceType.objects.count() == 1
    assert Feature.objects.count() == 1


def test_feature_ahti_id_field():
    f = FeatureFactory()

    assert f.ahti_id == f"{f.source_type.system}:{f.source_type.type}:{f.source_id}"


def test_feature_ahti_id_filter():
    f = FeatureFactory()
    f_fetched = Feature.objects.ahti_id(f.ahti_id)
    assert f.pk == f_fetched.pk


def test_feature_ahti_id_does_not_exist():
    with pytest.raises(Feature.DoesNotExist):
        Feature.objects.ahti_id("Nope")


def test_image():
    ImageFactory()

    assert Feature.objects.count() == 1
    assert Image.objects.count() == 1
    assert License.objects.count() == 1


def test_license():
    LicenseFactory()

    assert License.objects.count() == 1


def test_link():
    LinkFactory()

    assert Link.objects.count() == 1
    assert Feature.objects.count() == 1


def test_tag():
    TagFactory()

    assert Tag.objects.count() == 1


def test_contact_info():
    ContactInfoFactory()

    assert ContactInfo.objects.count() == 1
    assert Feature.objects.count() == 1


def test_opening_hours_period():
    OpeningHoursPeriodFactory()

    assert OpeningHoursPeriod.objects.count() == 1
    assert Feature.objects.count() == 1


def test_opening_hours():
    OpeningHoursFactory()

    assert OpeningHours.objects.count() == 1
    assert OpeningHoursPeriod.objects.count() == 1
    assert Feature.objects.count() == 1


def test_override():
    OverrideFactory()

    assert Override.objects.count() == 1
    assert Feature.objects.count() == 1
