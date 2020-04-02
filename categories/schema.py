import graphene
from django.utils.translation import gettext_lazy as _
from graphene_django import DjangoObjectType

from categories import models


class FeatureCategory(DjangoObjectType):
    class Meta:
        model = models.Category
        fields = (
            "id",
            "features",
        )

    name = graphene.String(required=True)
    description = graphene.String()


class Query(graphene.ObjectType):
    feature_categories = graphene.List(
        FeatureCategory, description=_("Retrieve all categories")
    )

    def resolve_feature_categories(self, info, **kwargs):
        return models.Category.objects.all()
