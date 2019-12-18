import graphene

import features.schema


class Query(features.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
