import graphene

from domain.prom_code import GeneratePromoCodeResult
from domain import prom_code
from .common_types import ErrorResult


class CodeGenerationInput(graphene.InputObjectType):
    event_id = graphene.Int(required=True)
    amount = graphene.Int(required=True)
    radius = graphene.Float(required=False)
    credit = graphene.Float(required=False)
    expiration_time = graphene.DateTime(required=True)


class CodeGenerationOutput(graphene.ObjectType):
    codes = graphene.List(graphene.String)
    status = graphene.Int()


class CodesResult(graphene.Union):
    class Meta:
        types = (CodeGenerationOutput, ErrorResult)


class CreateCodes(graphene.Mutation):
    class Arguments:
        data = CodeGenerationInput(required=True)

    result = graphene.Field(CodesResult)

    def mutate(root, info, data):
        """
        Input example:

mutation myFirstMutation {
    createCodes(data: {eventId: 1, amount: 2, radius: 3.2, expirationTime: "2019-09-21T18:35:50.184Z"}) {
      result{
        ... on CodeGenerationOutput{
          codes
          status
        }
        ... on ErrorResult{
          reason
          status
        }
      }
    }
}

Responses example:

{
  "data": {
    "createCodes": {
      "result": {
        "codes": [
          "cY0iBcEkXhO1",
          "ygeM5alzitAh"
        ],
        "status": 0
      }
    }
  }
}

{
  "data": {
    "createCodes": {
      "result": {
        "msg": "The event do not exists",
        "status": 1
      }
    }
  }
}

        :param info:
        :param data:
        :return:
        """
        relation = {
            GeneratePromoCodeResult.EventDoNotExists:
            lambda _: ErrorResult("The event do not exists", 1),
            GeneratePromoCodeResult.Ok:
            lambda pcodes: CodeGenerationOutput(
                list(map(lambda pcode: pcode.code, pcodes)), 0),
        }
        code, res = prom_code.generate_promo_code(
            data.event_id, data.amount, {
                'radius': data.radius,
                'credit': data.credit,
                'expiration_time': data.expiration_time,
            })
        return CreateCodes(result=relation[code](res))
