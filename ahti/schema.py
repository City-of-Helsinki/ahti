import graphene
from django.conf import settings
from graphene_django.debug import DjangoDebug

import categories.schema
import features.schema

Query = type(
    "Query",
    (features.schema.Query, categories.schema.Query, graphene.ObjectType),
    {"debug": graphene.Field(DjangoDebug, name="_debug")} if settings.DEBUG else {},
)


schema = graphene.Schema(query=Query)
