import graphene
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from graphene_django.debug import DjangoDebug

import categories.schema
import features.schema

_debug = {"debug": graphene.Field(DjangoDebug, name="_debug")}
_default = {"__doc__": _("Ahti GraphQL API queries")}

Query = type(
    "Query",
    (features.schema.Query, categories.schema.Query, graphene.ObjectType),
    {**_debug, **_default} if settings.DEBUG else _default,
)


schema = graphene.Schema(query=Query)
