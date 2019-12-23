import graphene
import graphql_geojson
from django.apps import apps
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from features import models


class SourceType(DjangoObjectType):
    class Meta:
        model = models.SourceType
        interfaces = (relay.Node,)


class FeatureTranslations(DjangoObjectType):
    class Meta:
        model = apps.get_model("features", "FeatureTranslation")


class Feature(graphql_geojson.GeoJSONType):
    class Meta:
        fields = (
            "id",
            "geometry",
            "created_at",
            "translations",
            "source_type",
        )
        model = models.Feature
        geojson_field = "geometry"
        interfaces = (relay.Node,)

    ahti_id = graphene.String(required=True)
    name = graphene.String()
    url = graphene.String()
    modified_at = graphene.DateTime(required=True)

    def resolve_modified_at(self: models.Feature, info, **kwargs):
        return self.mapped_at


class Query(graphene.ObjectType):
    features = DjangoConnectionField(Feature)

    def resolve_features(self, info, **kwargs):
        return models.Feature.objects.all()
