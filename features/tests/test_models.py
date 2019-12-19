import pytest

from features.models import Feature, SourceType
from features.tests.factories import FeatureFactory, SourceTypeFactory


@pytest.mark.django_db
def test_source_type():
    SourceTypeFactory()

    assert SourceType.objects.count() == 1


@pytest.mark.django_db
def test_feature():
    FeatureFactory()

    assert SourceType.objects.count() == 1
    assert Feature.objects.count() == 1
