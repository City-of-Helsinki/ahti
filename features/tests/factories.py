import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory.random import randgen

from features.enums import FeatureDetailsType, OverrideFieldType
from features.models import (
    ContactInfo,
    Feature,
    FeatureDetails,
    FeatureTeaser,
    Image,
    License,
    Link,
    OpeningHours,
    OpeningHoursPeriod,
    Override,
    SourceType,
    Tag,
)


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
    one_liner = factory.Sequence(lambda n: "Place %d one-liner" % n)
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


class FeatureTeaserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeatureTeaser

    feature = factory.SubFactory(FeatureFactory)
    header = "Starting from:"
    main = "7 euro a day."


class FeatureDetailsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeatureDetails

    feature = factory.SubFactory(FeatureFactory)
    type = factory.Faker("random_element", elements=list(FeatureDetailsType))


class LicenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = License

    name = factory.Sequence(lambda n: "License %d" % n)


class LinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Link

    feature = factory.SubFactory(FeatureFactory)
    type = factory.Faker("slug")
    url = factory.Faker("url")


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


class ContactInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactInfo

    feature = factory.SubFactory(FeatureFactory)
    street_address = factory.Faker("address")
    postal_code = factory.Faker("postcode", locale="fi_FI")
    municipality = factory.Faker("city", locale="fi_FI")
    phone_number = factory.Faker("phone_number")
    email = factory.Faker("company_email")


class OpeningHoursPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OpeningHoursPeriod

    feature = factory.SubFactory(FeatureFactory)
    valid_from = factory.Faker("date_between", start_date="-1y", end_date="today")
    valid_to = factory.Faker("date_between", start_date="today", end_date="+1y")


class OpeningHoursFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OpeningHours

    period = factory.SubFactory(OpeningHoursPeriodFactory)
    day = factory.Faker("pyint", min_value=1, max_value=7)
    opens = factory.Faker("time_object")
    closes = factory.Faker("time_object")


class OverrideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Override

    feature = factory.SubFactory(FeatureFactory)
    field = factory.Faker("random_element", elements=OverrideFieldType)
