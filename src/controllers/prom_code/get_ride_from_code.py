from flask_restplus import Resource, fields
import datetime

from . import api

from domain.prom_code import RideFromPromCodeResult
from domain import prom_code

getRideFromPromoCodeModelDict = {
    'code': fields.String(required=True),
    'origin_lat': fields.Float(required=True),
    'origin_lng': fields.Float(required=True),
    'dest_lat': fields.Float(required=True),
    'dest_lng': fields.Float(required=True),
}

GetRideFromPromoCodeModel = api.model('GetRideFromPromoCodeModel', getRideFromPromoCodeModelDict)


def get_ride_from_prom_code_controller(origin_lat, origin_lng, dest_lat, dest_lng, prom_code):
    """Docs."""
    template = "%Y-%m-%d"
    relation = {
        RideFromPromCodeResult.PromCodeDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The event do not exists"},

        RideFromPromCodeResult.PromCodeInactive:
            lambda _: {"status": "error",
                       "reason": "The Prom Code is Inactive"},

        RideFromPromCodeResult.PromCodeInvalid:
            lambda _: {"status": "error",
                       "reason": "The origin and the destination are to far from the event"},

        RideFromPromCodeResult.InsuficientCredit:
            lambda _: {"status": "error",
                       "reason": "The code's credit is insuficient for that ride"},

        RideFromPromCodeResult.Ok:
            lambda data: {"status": "ok",
                          "code": data["code"].code,
                          "remaining_credit": data["code"].credit,
                          "event_id": data["code"].event_id,
                          "expiration_time": datetime.datetime.strftime(data["code"].expiration_time, template),
                          "polyline": data["polyline"]
                          },
    }
    code, res = prom_code.get_ride_from_prom_code(origin_lat, origin_lng, dest_lat, dest_lng, prom_code)
    return relation[code](res)


@api.route('/get-ride')
class GetRideFromPromoCode(Resource):
    """Docs."""

    @api.expect(GetRideFromPromoCodeModel, validate=True)
    def post(self):
        """Docs."""
        data = api.payload
        code = data["code"]
        origin_lat = data["origin_lat"]
        origin_lng = data["origin_lng"]
        dest_lat = data["dest_lat"]
        dest_lng = data["dest_lng"]
        return get_ride_from_prom_code_controller(origin_lat, origin_lng, dest_lat, dest_lng, code)
