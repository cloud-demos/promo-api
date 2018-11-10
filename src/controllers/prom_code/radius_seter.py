from flask_restplus import Resource, fields
from flask_restplus import reqparse

from . import api

from domain.prom_code import SetRadiusFromEventsResult, SetRadiusResult
from domain import prom_code

setRadiusToEventModelDict = {
    'event_id': fields.Integer(required=True),
    'radius': fields.Float(required=True),
}
SetRadiusToEventModel = api.model('SetRadiusToEventModel', setRadiusToEventModelDict)


def set_radius_to_event_controller(event_id, radius):
    """Docs."""
    relation = {
        SetRadiusFromEventsResult.EventDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The event do not exists"},
        SetRadiusFromEventsResult.Ok:
            lambda event: {'status': "ok",
                           "event_name": event.name},
    }
    code, res = prom_code.set_radius_to_event(event_id, radius)
    return relation[code](res)


@api.route('/set-radius-to-event')
class SetRadiusToEvent(Resource):
    """Docs."""

    @api.expect(SetRadiusToEventModel, validate=True)
    def post(self):
        """Docs."""
        data = api.payload
        event_id = data["event_id"]
        radius = data["radius"]
        return set_radius_to_event_controller(event_id, radius)



spreadRadiusInEventModelDict = {
    'event_id': fields.Integer(required=True),
}
SpreadRadiusInEventModel = api.model('SpreadRadiusInEventModel', spreadRadiusInEventModelDict)


def spread_radius_in_event_controller(event_id):
    """Docs."""
    relation = {
        SetRadiusFromEventsResult.EventDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The event do not exists"},
        SetRadiusFromEventsResult.Ok:
            lambda event: {'status': "ok",
                           "event_name": event.name},
    }
    code, res = prom_code.spread_radius_from_event_to_all_prom_codes(event_id)
    return relation[code](res)


@api.route('/spread-radius-in-event')
class SpreadRadiusInEvent(Resource):
    """Docs."""

    @api.expect(SpreadRadiusInEventModel, validate=True)
    def post(self):
        """Docs."""
        data = api.payload
        event_id = data["event_id"]
        return spread_radius_in_event_controller(event_id)




setRadiusToPromCodeModelDict = {
    'code': fields.String(required=True),
    'radius': fields.Float(required=True),
}
SetRadiusToPromCodeModel = api.model('SetRadiusToPromCodeModel', setRadiusToPromCodeModelDict)


def set_radius_to_prom_code_controller(code, radius):
    """Docs."""
    relation = {
        SetRadiusResult.PromCodeDoNotExists:
            lambda _: {"status": "error",
                       "reason": "The code do not exists"},
        SetRadiusResult.Ok:
            lambda pcode: {"status": "ok",
                           "code": pcode.code},
    }
    code_result, res = prom_code.set_radius_to_prom_code(code, radius)
    return relation[code_result](res)


@api.route('/set-radius-to-prom-code')
class SetRadiusToPromCode(Resource):
    """Docs."""

    @api.expect(SetRadiusToPromCodeModel, validate=True)
    def post(self):
        """Docs."""
        data = api.payload
        code = data["code"]
        radius = data["radius"]
        return set_radius_to_prom_code_controller(code, radius)


