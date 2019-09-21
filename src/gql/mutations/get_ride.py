import graphene
import logging

from domain.prom_code import RideFromPromCodeResult
from domain import prom_code
from .common_types import ErrorResult


class GetRideFromPromoCodeInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    origin_lat = graphene.Float(required=True)
    origin_lng = graphene.Float(required=True)
    dest_lat = graphene.Float(required=True)
    dest_lng = graphene.Float(required=True)


class RideFromPromoCodeOutput(graphene.ObjectType):
    code = graphene.String()
    remaining_credit = graphene.Float()
    event_id = graphene.Int()
    expiration_time = graphene.DateTime()
    polyline = graphene.String()
    status = graphene.Int()


class RideFromPromoCodeResult(graphene.Union):
    class Meta:
        types = (RideFromPromoCodeOutput, ErrorResult)


class GetRideFromPromoCode(graphene.Mutation):
    class Arguments:
        data = GetRideFromPromoCodeInput(required=True)

    result = graphene.Field(RideFromPromoCodeResult)

    def mutate(root, info, data):
        """

mutation myFirstMutation {
   getRide(data: {code: "ZUF1g8cbNdcc", originLat: 2, originLng: 2, destLat: 0, destLng: 0}){
    result{
        ... on RideFromPromoCodeOutput{
          code
          remainingCredit
          expirationTime
          polyline
          eventId
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
    "getRide": {
      "result": {
        "code": "ZUF1g8cbNdcc",
        "remainingCredit": 341758.086440011,
        "expirationTime": "2019-10-14T21:35:09.172000",
        "polyline": "_seK_seK~reK~reK",
        "eventId": 1,
        "status": 0
      }
    }
  }
}


{
  "data": {
    "getRide": {
      "result": {
        "msg": "The Prom Code do not exists",
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
            RideFromPromCodeResult.PromCodeDoNotExists:
            lambda _: ErrorResult("The Prom Code do not exists", 1),
            RideFromPromCodeResult.PromCodeInactive:
            lambda _: ErrorResult("The Prom Code is Inactive", 2),
            RideFromPromCodeResult.PromCodeInvalid:
            lambda _: ErrorResult(
                "The origin and the destination are to far from the event", 3),
            RideFromPromCodeResult.InsuficientCredit:
            lambda _: ErrorResult(
                "The code's credit is insuficient for that ride", 4),
            RideFromPromCodeResult.PromCodeExpired:
            lambda _: ErrorResult("The code is expired", 5),
            RideFromPromCodeResult.Ok:
            lambda data: RideFromPromoCodeOutput(
                code=data["code"].code,
                remaining_credit=data["code"].credit,
                event_id=data["code"].event_id,
                expiration_time=data["code"].expiration_time,
                polyline=data["polyline"],
                status=0)
        }
        response_code, res = prom_code.get_ride_from_prom_code(
            data.origin_lat, data.origin_lng, data.dest_lat, data.dest_lng,
            data.code)
        return GetRideFromPromoCode(result=relation[response_code](res))
