from flask_restplus import Resource, fields
from flask_restplus import reqparse
import logging

from domain import prom_code
from . import api

promoCodeModelDict = {
    'expiration_time': fields.DateTime(dt_format='rfc822'),
    'event_id': fields.Integer(),
    'active': fields.Boolean(),
    'radius': fields.Float(),
    'code': fields.String(),
    'credit': fields.Float(),
    'id': fields.Integer(),
}
PromoCodeModel = api.model('PromoCodeModel', promoCodeModelDict)

getPromoCodeModelDict = {
    'pages': fields.Integer(),
    'items': fields.List(fields.Nested(PromoCodeModel)),
}
GetPromoCodeModel = api.model('GetPromoCodeModel', getPromoCodeModelDict)

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('event_id',
                               type=int,
                               location='args',
                               required=True)
pagination_parser.add_argument('page',
                               type=int,
                               location='args',
                               required=False,
                               default=1)

pagination_parser.add_argument('page_length',
                               type=int,
                               location='args',
                               required=False,
                               default=10)


@api.route('/list-active')
class PromCodeActiveList(Resource):
    @api.marshal_with(GetPromoCodeModel, code=200, skip_none=True)
    @api.expect(pagination_parser, validate=True)
    def get(self):
        """
        The active codes

        Returns the active codes of an specific event_id

        It allows pagination using the "page" query parameter.
        """
        args = pagination_parser.parse_args()
        event_id = args["event_id"]
        page = args.get('page')
        page_length = args.get('page_length')

        logging.info(
            f"Geting the active codes of event: {event_id}, page: {page}, page length: {page_length}"
        )
        return prom_code.get_active_promo_codes(event_id, page, page_length)


@api.route('/list')
class PromCodeList(Resource):
    @api.marshal_with(GetPromoCodeModel, code=200, skip_none=True)
    @api.expect(pagination_parser, validate=True)
    def get(self):
        """
        All the codes

        Returns the codes of an specific event_id

        It allows pagination using the "page" query parameter.
        """
        args = pagination_parser.parse_args()
        event_id = args["event_id"]
        page = args.get('page')
        page_length = args.get('page_length')

        logging.info(
            f"Geting all the codes of event: {event_id}, page: {page}, page length: {page_length}"
        )
        return prom_code.get_all_promo_codes(event_id, page, page_length)
