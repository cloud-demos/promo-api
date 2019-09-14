from flask_restplus import Resource, fields
import logging

from . import api

from domain.prom_code import GeneratePromoCodeResult
from domain import prom_code

promoCodeCreationModelDict = {
    'event_id': fields.Integer(required=True),
    'amount': fields.Integer(required=True),
    'radius': fields.Float(required=False),
    'credit': fields.Float(required=False),
    'expiration_time': fields.DateTime(required=False, dt_format='rfc822'),
}
PromoCodeCreationModel = api.model('PromoCodeCreationModel',
                                   promoCodeCreationModelDict)


def generate_promo_code_controller(event_id, amount, data):
    relation = {
        GeneratePromoCodeResult.EventDoNotExists: lambda _: {
            "status": "error",
            "reason": "The event do not exists"
        },
        GeneratePromoCodeResult.Ok: lambda pcodes: {
            "status": "ok",
            "codes": list(map(lambda pcode: pcode.code, pcodes))
        },
    }
    code, res = prom_code.generate_promo_code(event_id, amount, data)
    return relation[code](res)


@api.route('/generate')
class PromCodeGenerate(Resource):
    """
        Endpoint to generate promotional codes
    """
    @api.expect(PromoCodeCreationModel, validate=True)
    def post(self):
        """
            Promotional code generation
        """
        data = api.payload
        event_id = data["event_id"]
        amount = data["amount"]
        del data["event_id"]
        del data["amount"]

        logging.info(
            f"Generating {amount} promotional codes for the event: {event_id}")
        return generate_promo_code_controller(event_id, amount, data)
