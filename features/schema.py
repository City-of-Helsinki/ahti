import graphene
import graphql_geojson
from django.apps import apps
from graphene import ObjectType, relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from features import models


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
        fields = ("name",)

    name = graphene.String()


class Feature(graphql_geojson.GeoJSONType):
    class Meta:
        fields = (
            "id",
            "geometry",
            "created_at",
            "translations",
            "images",
        )
        model = models.Feature
        geojson_field = "geometry"
        interfaces = (relay.Node,)

    ahti_id = graphene.String(required=True)
    source = graphene.Field(FeatureSource, required=True)
    name = graphene.String()
    url = graphene.String()
    modified_at = graphene.DateTime(required=True)

    def resolve_source(self: models.Feature, info, **kwargs):
        return {
            "system": self.source_type.system,
            "type": self.source_type.type,
            "id": self.source_id,
        }

    def resolve_modified_at(self: models.Feature, info, **kwargs):
        return self.mapped_at


class Query(graphene.ObjectType):
    features = DjangoConnectionField(Feature)

    def resolve_features(self, info, **kwargs):
        return models.Feature.objects.all()
