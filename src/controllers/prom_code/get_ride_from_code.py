from flask_restplus import Resource, fields
import datetime
import logging

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

GetRideFromPromoCodeModel = api.model('GetRideFromPromoCodeModel',
                                      getRideFromPromoCodeModelDict)


def get_ride_from_prom_code_controller(
        origin_lat, origin_lng, dest_lat, dest_lng, code):
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
                       "reason": "The origin and the destination are to far "
                                 "from the event"},

        RideFromPromCodeResult.InsuficientCredit:
            lambda _: {"status": "error",
                       "reason": "The code's credit is insuficient for "
                                 "that ride"},

        RideFromPromCodeResult.PromCodeExpired:
            lambda _: {"status": "error",
                       "reason": "The code is expired"},

        RideFromPromCodeResult.Ok:
            lambda data: {"status": "ok",
                          "code": data["code"].code,
                          "remaining_credit": data["code"].credit,
                          "event_id": data["code"].event_id,
                          "expiration_time": datetime.datetime.strftime(
                              data["code"].expiration_time, template),
                          "polyline": data["polyline"]
                          },
    }

    response_code, res = prom_code.get_ride_from_prom_code(
        origin_lat, origin_lng, dest_lat, dest_lng, code)
    return relation[response_code](res)


@api.route('/get-ride')
class GetRideFromPromCode(Resource):
    """
        Get a ride using a promotional code.

        Several constraints are used
    """

    @api.expect(GetRideFromPromoCodeModel, validate=True)
    def post(self):
        """
            Get a ride using a promotional code

            Several constraints are used and can be response errors:
                . The event do not exists
                . The Prom Code is Inactive
                . The origin and the destination are to far from the event
                . The code's credit is insuficient for that ride
                . The code is expired

            When the request is ok the response includes a polyline with
            origin and destination coordinates and several data about the code.
        """
        data = api.payload
        code = data["code"]
        origin_lat = data["origin_lat"]
        origin_lng = data["origin_lng"]
        dest_lat = data["dest_lat"]
        dest_lng = data["dest_lng"]

        logging.info(f"Geting a ride using the promotional code {code}")
        return get_ride_from_prom_code_controller(
            origin_lat, origin_lng, dest_lat, dest_lng, code)
