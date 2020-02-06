import graphene
import graphql_geojson
from django.apps import apps
from graphene import ObjectType, relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from features import models
from features.enums import OverrideFieldType, Weekday

WeekdayEnum = graphene.Enum.from_enum(
    Weekday, description=lambda e: e.label if e else ""
)


class Address(ObjectType):
    street_address = graphene.String()
    postal_code = graphene.String()
    municipality = graphene.String()


class ContactInfo(DjangoObjectType):
    class Meta:
        model = models.ContactInfo
        fields = ("email", "phone_number")

    address = graphene.Field(Address)

    def resolve_address(self: models.ContactInfo, info, **kwargs):
        return {
            "street_address": self.street_address,
            "postal_code": self.postal_code,
            "municipality": self.municipality,
        }


class FeatureSource(ObjectType):
    """Source information for a feature."""

    system = graphene.String(required=True)
    type = graphene.String(required=True)
    id = graphene.String(
        required=True, description="ID of the current feature in source system"
    )


class FeatureTranslations(DjangoObjectType):
    class Meta:
        model = apps.get_model("features", "FeatureTranslation")
        exclude = ("id", "master")


class Image(DjangoObjectType):
    class Meta:
        model = models.Image
        fields = (
            "url",
            "copyright_owner",
            "license",
        )


class License(DjangoObjectType):
    class Meta:
        model = models.License
        fields = ("id",)

    name = graphene.String(required=True)


class Tag(DjangoObjectType):
    class Meta:
        model = models.Tag
        fields = ("id",)

    name = graphene.String(required=True)


class OpeningHoursPeriod(DjangoObjectType):
    class Meta:
        model = models.OpeningHoursPeriod
        fields = (
            "valid_from",
            "valid_to",
            "opening_hours",
        )

    comment = graphene.String()


class OpeningHours(DjangoObjectType):
    class Meta:
        model = models.OpeningHours
        fields = (
            "opens",
            "closes",
            "all_day",
        )

    day = WeekdayEnum(required=True)


class Feature(graphql_geojson.GeoJSONType):
    class Meta:
        fields = (
            "id",
            "category",
            "created_at",
            "contact_info",
            "geometry",
            "images",
            "opening_hours_periods",
            "tags",
            "translations",
        )
        model = models.Feature
        geojson_field = "geometry"
        interfaces = (relay.Node,)

    ahti_id = graphene.String(required=True)
    source = graphene.Field(FeatureSource, required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    url = graphene.String()
    modified_at = graphene.DateTime(required=True)
    parents = graphene.List("features.schema.Feature", required=True)
    children = graphene.List("features.schema.Feature", required=True)

    def resolve_source(self: models.Feature, info, **kwargs):
        return {
            "system": self.source_type.system,
            "type": self.source_type.type,
            "id": self.source_id,
        }

    def resolve_name(self: models.Feature, info, **kwargs):
        name_override = self.overrides.filter(field=OverrideFieldType.NAME).first()
        if name_override:
            return name_override.value
        return self.name

    def resolve_modified_at(self: models.Feature, info, **kwargs):
        latest_override = self.overrides.order_by("-modified_at").first()
        return (
            max(self.mapped_at, latest_override.modified_at)
            if latest_override
            else self.mapped_at
        )

    def resolve_parents(self: models.Feature, info, **kwargs):
        return self.parents.all()

    def resolve_children(self: models.Feature, info, **kwargs):
        return self.children.all()


class Query(graphene.ObjectType):
    features = DjangoConnectionField(Feature)

    def resolve_features(self, info, **kwargs):
        return models.Feature.objects.all()
