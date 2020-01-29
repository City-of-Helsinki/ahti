import graphene

import categories.schema
import features.schema


class Query(features.schema.Query, categories.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
