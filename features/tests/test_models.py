import pytest

from features.models import ContactInfo, Feature, Image, License, SourceType, Tag
from features.tests.factories import (
    ContactInfoFactory,
    FeatureFactory,
    ImageFactory,
    LicenseFactory,
    SourceTypeFactory,
    TagFactory,
)


@pytest.mark.django_db
def test_source_type():
    SourceTypeFactory()

    assert SourceType.objects.count() == 1


@pytest.mark.django_db
def test_feature():
    FeatureFactory()

    assert SourceType.objects.count() == 1
    assert Feature.objects.count() == 1
    f = Feature.objects.first()
    assert f.ahti_id == f"{f.source_type.system}:{f.source_type.type}:{f.source_id}"


@pytest.mark.django_db
def test_image():
    ImageFactory()

    assert Feature.objects.count() == 1
    assert Image.objects.count() == 1
    assert License.objects.count() == 1


@pytest.mark.django_db
def test_license():
    LicenseFactory()

    assert License.objects.count() == 1


@pytest.mark.django_db
def test_tag():
    TagFactory()

    assert Tag.objects.count() == 1


@pytest.mark.django_db
def test_contact_info():
    ContactInfoFactory()

    assert ContactInfo.objects.count() == 1
    assert Feature.objects.count() == 1
