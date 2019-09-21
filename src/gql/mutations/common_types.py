import graphene


class ErrorResult(graphene.ObjectType):
    reason = graphene.String()
    status = graphene.Int()
