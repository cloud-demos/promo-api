import graphene
import logging

from domain.prom_code import PromoCodeResult
from domain import prom_code
from .common_types import ErrorResult


class StatusCodeInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    active = graphene.Boolean(required=True)


class StatusCodeOutput(graphene.ObjectType):
    code = graphene.String()
    status = graphene.Int()


class StatusCodeResult(graphene.Union):
    class Meta:
        types = (StatusCodeOutput, ErrorResult)


class StateCode(graphene.Mutation):
    class Arguments:
        data = StatusCodeInput(required=True)

    result = graphene.Field(StatusCodeResult)

    def mutate(root, info, data):
        """
mutation myFirstMutation {
   state(data: {code: "ZUF1g8cbNdcc", active: false}){
     result{
        ... on StatusCodeOutput{
          code
          status
        }
        ... on ErrorResult{
          reason
          status
        }
      }
  }
}

{
  "data": {
    "state": {
      "result": {
        "code": "ZUF1g8cbNdcc",
        "status": 0
      }
    }
  }
}

{
  "data": {
    "state": {
      "result": {
        "msg": "The code do not exists",
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
            PromoCodeResult.PromoCodeDoNotExists:
            lambda _: ErrorResult("The code do not exists", 1),
            PromoCodeResult.Ok:
            lambda pcode: StatusCodeOutput(pcode.code, 0),
        }
        if data.active:
            response_code, res = prom_code.activate_promo_code(data.code)
        else:
            response_code, res = prom_code.deactivate_promo_code(data.code)
        return StateCode(result=relation[response_code](res))
