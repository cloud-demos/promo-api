import graphene
import logging

from domain.prom_code import SetRadiusFromEventsResult, SetRadiusResult
from domain import prom_code

from .common_types import ErrorResult


class SetRadiusToEventInput(graphene.InputObjectType):
    event_id = graphene.Int(required=True)
    radius = graphene.Float(required=True)


class SetRadiusToEventOutput(graphene.ObjectType):
    event_name = graphene.String()
    status = graphene.Int()


class SetRadiusToEventResult(graphene.Union):
    class Meta:
        types = (SetRadiusToEventOutput, ErrorResult)


class SetRadiusToEvent(graphene.Mutation):
    class Arguments:
        data = SetRadiusToEventInput(required=True)

    result = graphene.Field(SetRadiusToEventResult)

    def mutate(root, info, data):
        """
         mutation myFirstMutation {
  radiusToEvent(data: {eventId: 1, radius: 1212.88}){
    result{
        ... on SetRadiusToEventOutput{
          eventName
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
    "radiusToEvent": {
      "result": {
        "eventName": "EEEE",
        "status": 0
      }
    }
  }
}

{
  "data": {
    "radiusToEvent": {
      "result": {
        "reason": "The event do not exists",
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
            SetRadiusFromEventsResult.EventDoNotExists:
            lambda _: ErrorResult("The event do not exists", 1),
            SetRadiusFromEventsResult.Ok:
            lambda event: SetRadiusToEventOutput(event.name, 0),
        }
        response_code, res = prom_code.set_radius_to_event(
            data.event_id, data.radius)
        return SetRadiusToEvent(result=relation[response_code](res))


class SetRadiusToPromCodeInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    radius = graphene.Float(required=True)


class SetRadiusToPromCodeOutput(graphene.ObjectType):
    code = graphene.String()
    status = graphene.Int()


class SetRadiusToPromCodeResult(graphene.Union):
    class Meta:
        types = (SetRadiusToPromCodeOutput, ErrorResult)


class SetRadiusToPromCode(graphene.Mutation):
    class Arguments:
        data = SetRadiusToPromCodeInput(required=True)

    result = graphene.Field(SetRadiusToPromCodeResult)

    def mutate(root, info, data):
        """
mutation myFirstMutation {

   radiusToCode(data: {code: "ZUF1g8cbNdcc", radius: 1212.88}){
    result{
        ... on SetRadiusToPromCodeOutput{
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
    "radiusToCode": {
      "result": {
        "code": "ZUF1g8cbNdcc",
        "status": 0
      }
    }
  }
}
{
  "data": {
    "radiusToCode": {
      "result": {
        "reason": "The code do not exists",
        "status": 1
      }
    }
  }
}
        """
        relation = {
            SetRadiusResult.PromCodeDoNotExists:
            lambda _: ErrorResult("The code do not exists", 1),
            SetRadiusResult.Ok:
            lambda pcode: SetRadiusToPromCodeOutput(pcode.code, 0),
        }
        response_code, res = prom_code.set_radius_to_prom_code(
            data.code, data.radius)
        return SetRadiusToEvent(result=relation[response_code](res))


class SpreadRadiusToEventInput(graphene.InputObjectType):
    event_id = graphene.Int(required=True)


class SpreadRadiusToEventOutput(graphene.ObjectType):
    promo_codes_affected = graphene.Int()
    status = graphene.Int()


class SpreadRadiusToEventResult(graphene.Union):
    class Meta:
        types = (SpreadRadiusToEventOutput, ErrorResult)


class SpreadRadiusToEvent(graphene.Mutation):
    class Arguments:
        data = SpreadRadiusToEventInput(required=True)

    result = graphene.Field(SpreadRadiusToEventResult)

    def mutate(root, info, data):
        """
 mutation myFirstMutation {

   spreadRadiusInEvent(data: {eventId: 1}){
    result{
        ... on SpreadRadiusToEventOutput{
          promoCodesAffected
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
    "spreadRadiusInEvent": {
      "result": {
        "promoCodesAffected": 95,
        "status": 0
      }
    }
  }
}

   {
  "data": {
    "spreadRadiusInEvent": {
      "result": {
        "reason": "The event do not exists",
        "status": 1
      }
    }
  }
}
        """
        relation = {
            SetRadiusFromEventsResult.EventDoNotExists:
            lambda _: ErrorResult("The event do not exists", 1),
            SetRadiusFromEventsResult.Ok:
            lambda promo_codes_affected: SpreadRadiusToEventOutput(
                promo_codes_affected, 0),
        }
        response_code, res = prom_code.spread_radius_from_event_to_all_prom_codes(
            data.event_id)
        return SetRadiusToEvent(result=relation[response_code](res))
