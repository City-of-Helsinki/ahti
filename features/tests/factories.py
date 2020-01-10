import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory.random import randgen

from features.models import Feature, Image, License, SourceType, Tag


class SourceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SourceType

    system = factory.Faker("word")
    type = factory.Faker("word")


class FeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feature

    name = factory.Sequence(lambda n: "Place %d" % n)
    description = factory.Sequence(lambda n: "Place %d description" % n)
    url = factory.Faker("url")
    source_id = factory.Sequence(lambda n: "sid%d" % n)
    source_type = factory.SubFactory(SourceTypeFactory)
    source_modified_at = factory.LazyFunction(timezone.now)
    mapped_at = factory.LazyFunction(timezone.now)
    geometry = factory.LazyFunction(
        lambda: Point(
            24.915 + randgen.uniform(0, 0.040), 60.154 + randgen.uniform(0, 0.022)
        )
    )


class LicenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = License

    name = factory.Sequence(lambda n: "License %d" % n)


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image

    url = factory.Faker("image_url")
    copyright_owner = factory.Faker("name")
    feature = factory.SubFactory(FeatureFactory)
    license = factory.SubFactory(LicenseFactory)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    id = factory.Sequence(lambda n: "ahti:tag:%d" % n)
    name = factory.Sequence(lambda n: "Tag %d" % n)
