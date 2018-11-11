from flask_restplus import Resource, fields
from flask_restplus import reqparse

from domain import prom_code
from . import api

getPromoCodeModelDict = {
    'expiration_time': fields.DateTime(dt_format='rfc822'),
    'event_id': fields.Integer(),
    'active': fields.Boolean(),
    'radius': fields.Float(),
    'code': fields.String(),
    'credit': fields.Float(),
    'id': fields.Integer(),
}
GetPromoCodeModel = api.model('GetPromoCodeModel', getPromoCodeModelDict)

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('event_id', type=int, location='args',
                               required=True)
pagination_parser.add_argument('page', type=int, location='args',
                               required=False, default=1)


@api.route('/list-active')
class PromCodeActiveList(Resource):

    @api.marshal_with(GetPromoCodeModel, code=200, skip_none=True)
    def get(self):
        """
        The active codes


        Returns the active codes of an specific event_id

        It allows pagination using the "page" query parameter.

        """
        args = pagination_parser.parse_args()
        event_id = args["event_id"]
        page = args.get('page')
        return prom_code.get_active_promo_codes(event_id, page)


@api.route('/list')
class PromCodeList(Resource):

    @api.marshal_with(GetPromoCodeModel, code=200, skip_none=True)
    def get(self):
        """
        All the codes


        Returns the codes of an specific event_id

        It allows pagination using the "page" query parameter.

        """
        args = pagination_parser.parse_args()
        event_id = args["event_id"]
        page = args.get('page')
        return prom_code.get_all_promo_codes(event_id, page)
