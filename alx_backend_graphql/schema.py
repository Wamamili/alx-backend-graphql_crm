import graphene
from crm.schema import Query as CRMQuery  # 👈 import your crm app's Query

class Query(CRMQuery, graphene.ObjectType):
    """Root GraphQL query that includes CRM queries"""
    pass

schema = graphene.Schema(query=Query)
