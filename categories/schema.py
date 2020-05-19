import graphene
from django.utils.translation import gettext_lazy as _
from graphene_django import DjangoObjectType

from categories import models


class FeatureCategory(DjangoObjectType):
    """Category of a feature."""

    class Meta:
        model = models.Category
        fields = (
            "id",
            "features",
        )

    name = graphene.String(required=True, description=_("Display name of the category"))
    description = graphene.String(description=_("Category description"))


class Query(graphene.ObjectType):
    feature_categories = graphene.List(
        FeatureCategory, description=_("Retrieve all categories")
    )

    def resolve_feature_categories(self, info, **kwargs):
        return models.Category.objects.all()
