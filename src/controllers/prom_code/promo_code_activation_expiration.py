from flask_restplus import Resource, fields
from flask_restplus import reqparse

from . import api

from domain.prom_code import PromoCodeResult
from domain import prom_code

activation_parser = reqparse.RequestParser()
activation_parser.add_argument('code', type=str, location='args', required=True)


def deactivate_promo_code_controller(code):
    """Docs."""
    relation = {
        PromoCodeResult.PromoCodeDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The code do not exists"},
        PromoCodeResult.Ok:
            lambda pcode: {'status': "ok",
                           "code": pcode.code},
    }
    code, res = prom_code.deactivate_promo_code(code)
    return relation[code](res)


@api.route('/deactivate')
class PromCodeDeactivation(Resource):
    """Docs."""

    def put(self):
        """Docs."""
        args = activation_parser.parse_args()
        code = args['code']
        return deactivate_promo_code_controller(code)


def activate_promo_code_controller(code):
    """Docs."""
    relation = {
        PromoCodeResult.PromoCodeDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The code do not exists"},
        PromoCodeResult.Ok:
            lambda pcode: {'status': "ok",
                           "code": pcode.code},
    }
    code, res = prom_code.activate_promo_code(code)
    return relation[code](res)


@api.route('/activate')
class PromCodeActivation(Resource):
    """Docs."""

    def put(self):
        """Docs."""
        args = activation_parser.parse_args()
        code = args['code']
        return activate_promo_code_controller(code)


def promo_code_is_expired_controller(code):
    """Docs."""
    relation = {
        PromoCodeResult.PromoCodeDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The code do not exists"},
        PromoCodeResult.Ok:
            lambda result: {'status': "ok",
                           "expired": result},
    }
    code, res = prom_code.promo_code_is_expired(code)
    return relation[code](res)

@api.route('/expired')
class PromCodeExpired(Resource):
    """Docs."""

    def get(self):
        """Docs."""
        args = activation_parser.parse_args()
        code = args['code']
        return promo_code_is_expired_controller(code)
