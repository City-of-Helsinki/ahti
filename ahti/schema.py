import graphene
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from graphene_django.debug import DjangoDebug

import categories.schema
import features.schema

_query_debug = {"debug": graphene.Field(DjangoDebug, name="_debug")}
_query_default = {
    "__doc__": _("Ahti GraphQL API queries."),
}


class Mutation(
    features.schema.Mutation, graphene.ObjectType,
):
    """Ahti GraphQL API mutations."""


Query = type(
    "Query",
    (features.schema.Query, categories.schema.Query, graphene.ObjectType),
    {**_query_debug, **_query_default} if settings.DEBUG else _query_default,
)


schema = graphene.Schema(query=Query, mutation=Mutation)
