from flask_restplus import Resource, fields
from flask_restplus import reqparse

from . import api

from domain.prom_code import GeneratePromoCodeResult, generate_promo_code


promoCodeCreationModelDict = {
    'event_id': fields.Integer(required=True),
    'radius': fields.Float(required=False),
    'credit': fields.Float(required=False),
    'expiration_time': fields.DateTime(required=False, dt_format='rfc822'),
}
PromoCodeCreationModel = api.model('PromoCodeCreationModel', promoCodeCreationModelDict)



def generate_promo_code_controller(event_id, data):
    """Docs."""
    relation = {
        GeneratePromoCodeResult.EventDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The event do not exists"},
        GeneratePromoCodeResult.Ok:
            lambda pcode: {'status': "ok",
                           "code": pcode.code},
    }
    code, res = generate_promo_code(event_id, data)
    return relation[code](res)


@api.route('/generate')
class PromCodeGeneration(Resource):
    """Docs."""

    @api.expect(PromoCodeCreationModel, validate=True)
    def post(self):
        """Docs."""
        data = api.payload
        event_id = data["event_id"]
        del data["event_id"]
        return generate_promo_code_controller(event_id, data)
