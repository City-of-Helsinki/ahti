import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory.random import randgen

from features.models import Feature, SourceType


class SourceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SourceType

    system = factory.Faker("word")
    type = factory.Faker("word")


class FeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feature

    name = factory.Sequence(lambda n: "Place %d" % n)
    url = factory.Faker("uri")
    source_id = factory.Sequence(lambda n: "test:%d" % n)
    source_type = factory.SubFactory(SourceTypeFactory)
    source_modified_at = factory.LazyFunction(timezone.now)
    mapped_at = factory.LazyFunction(timezone.now)
    geometry = factory.LazyFunction(
        lambda: Point(
            24.915 + randgen.uniform(0, 0.040), 60.154 + randgen.uniform(0, 0.022)
        )
    )
