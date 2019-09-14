from flask_restplus import Resource
from flask_restplus import reqparse
import logging

from . import api

from domain.prom_code import PromoCodeResult
from domain import prom_code

activation_parser = reqparse.RequestParser()
activation_parser.add_argument('code',
                               type=str,
                               location='args',
                               required=True)


def deactivate_promo_code_controller(code):
    relation = {
        PromoCodeResult.PromoCodeDoNotExists: lambda _: {
            "status": "error",
            "reason": "The code do not exists"
        },
        PromoCodeResult.Ok: lambda pcode: {
            'status': "ok",
            "code": pcode.code
        },
    }
    code, res = prom_code.deactivate_promo_code(code)
    return relation[code](res)


@api.route('/deactivate')
class PromCodeDeactivation(Resource):
    def put(self):
        """
            Code deactivation

            Given a code this deactivate it.
            It requires a "code" query parameter.

        """
        args = activation_parser.parse_args()
        code = args['code']

        logging.info(f"Deactivation of the code {code}")
        return deactivate_promo_code_controller(code)


def activate_promo_code_controller(code):
    relation = {
        PromoCodeResult.PromoCodeDoNotExists: lambda _: {
            "status": "error",
            "reason": "The code do not exists"
        },
        PromoCodeResult.Ok: lambda pcode: {
            'status': "ok",
            "code": pcode.code
        },
    }
    code, res = prom_code.activate_promo_code(code)
    return relation[code](res)


@api.route('/activate')
class PromCodeActivation(Resource):
    def put(self):
        """
            Code activation

            Given a code this activate it.
            It requires a "code" query parameter.

        """
        args = activation_parser.parse_args()
        code = args['code']

        logging.info(f"Activation of the code {code}")
        return activate_promo_code_controller(code)


def promo_code_is_expired_controller(code):
    relation = {
        PromoCodeResult.PromoCodeDoNotExists: lambda _: {
            "status": "error",
            "reason": "The code do not exists"
        },
        PromoCodeResult.Ok: lambda result: {
            'status': "ok",
            "expired": result
        },
    }
    code, res = prom_code.promo_code_is_expired(code)
    return relation[code](res)


@api.route('/expired')
class PromCodeExpired(Resource):
    def get(self):
        """
            Code expiration query

            Given a code it respond about the "expired" state.
            It requires a "code" query parameter.

        """
        args = activation_parser.parse_args()
        code = args['code']

        logging.info(f"Checking the expiration status of the code {code}")
        return promo_code_is_expired_controller(code)
