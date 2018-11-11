from enum import Enum

from sqlalchemy import and_

import polyline
from geopy import distance

import config
from domain.models import PromCode, Event, db
from domain import utils

GeneratePromoCodeResult = Enum('GeneratePromoCodeResult',
                               'EventDoNotExists Ok')


def generate_promo_code(event_id, data={}):
    """
        The promotional code generation logic

    :param event_id: The target event of the codes
    :param data: Parameters to create the promotional code
    :return: (EventDoNotExists, None) | (Ok, pcode)
    """
    event = Event.query.get(event_id)
    if not event:
        return GeneratePromoCodeResult.EventDoNotExists, None

    pcode = True
    while pcode:
        code = utils.string_generator(config.CODE_LENGTH)
        pcode = db.session.query(PromCode).filter(PromCode.code == code) \
            .first()

    pcode = PromCode(
        event_id=event_id,
        credit=data.get("credit", config.DEFAULT_CREDIT),
        radius=data.get("radius", event.radius),
        expiration_time=data.get("expiration_time",
                                 utils.get_default_expiration_time()),
        code=code,
    )

    db.session.add(pcode)
    db.session.commit()

    return GeneratePromoCodeResult.Ok, pcode


PromoCodeResult = Enum('PromoCodeResult', 'PromoCodeDoNotExists Ok')


def promo_code_is_expired(code):
    """
        Checking the "expired" state of an code
    :param code: The code in question
    :return: (PromoCodeDoNotExists, None) | (Ok, <expired state>)
    """
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return PromoCodeResult.PromoCodeDoNotExists, None

    return PromoCodeResult.Ok, pcode.expired()


def deactivate_promo_code(code):
    """
        Code deactivation
    :param code: The code to deactivate
    :return: (PromoCodeDoNotExists, None) | (Ok, <updated code object>)
    """
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return PromoCodeResult.PromoCodeDoNotExists, None

    pcode.deactivate()

    return PromoCodeResult.Ok, pcode


def activate_promo_code(code):
    """
        Code activation
    :param code: The code to activate
    :return: (PromoCodeDoNotExists, None) | (Ok, <updated code object>)
    """
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return PromoCodeResult.PromoCodeDoNotExists, None

    pcode.activate()

    return PromoCodeResult.Ok, pcode


def get_all_promo_codes(event_id, page=1, page_length=50):
    """
        All the codes from an specific event
    :param event_id: The event to query
    :param page: Page number
    :param page_length: Page length
    :return: The corresponding page
    """
    offset = (page - 1) * page_length
    return db.session.query(PromCode).filter(
        PromCode.event_id == event_id).offset(offset).limit(page_length).all()


def get_active_promo_codes(event_id, page=1, page_length=50):
    """
        All the active codes from an specific event
    :param event_id: The event to query
    :param page: Page number
    :param page_length: Page length
    :return: The corresponding page
    """
    offset = (page - 1) * page_length
    return db.session.query(PromCode).filter(
        and_(PromCode.active, PromCode.event_id == event_id)) \
        .offset(offset).limit(page_length).all()


SetRadiusFromEventsResult = Enum('SetRadiusFromEventsResult',
                                 'EventDoNotExists Ok')


def set_radius_to_event(event_id, radius):
    """
        Changing the radius to an event
    :param event_id: The event to change
    :param radius: The new radius
    :return: (EventDoNotExists, None) | (Ok, <the event changed>)
    """
    event = Event.query.get(event_id)
    if not event:
        return SetRadiusFromEventsResult.EventDoNotExists, None

    event.set_radius(radius)

    return SetRadiusFromEventsResult.Ok, event


def spread_radius_from_event_to_all_prom_codes(event_id):
    """
        Sets the event radius to all his codes
    :param event_id: The event to process
    :return: (EventDoNotExists, None) | (Ok, <the event used>)
    """
    event = Event.query.get(event_id)
    if not event:
        return SetRadiusFromEventsResult.EventDoNotExists, None

    for pcode in event.prom_codes:
        pcode.set_radius(event.radius)

    return SetRadiusFromEventsResult.Ok, event


SetRadiusResult = Enum('SetRadiusResult', 'PromCodeDoNotExists Ok')


def set_radius_to_prom_code(code, radius):
    """
        To change the radius to a specific promotional code
    :param code: The code to update
    :param radius: The new radius
    :return: (PromCodeDoNotExists, None) | (Ok, <the code updated>)
    """
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return SetRadiusResult.PromCodeDoNotExists, None

    pcode.set_radius(radius)

    return SetRadiusResult.Ok, pcode


RideFromPromCodeResult = Enum('RideFromPromCodeResult',
                              'PromCodeDoNotExists '
                              'PromCodeInactive PromCodeInvalid '
                              'InsuficientCredit PromCodeExpired Ok')


def calculate_value(origin_lat, origin_lng, dest_lat, dest_lng):
    """
        A made up way to calculate the value of an specific ride.

    :return: <distance in miles> * <price of a mile>
    """
    dist = distance.distance(
        (origin_lat, origin_lng), (dest_lat, dest_lng)).miles
    return dist * config.MILES_COST


def get_ride_from_prom_code(origin_lat, origin_lng, dest_lat, dest_lng, code):
    """
        The logic to validate and to apply the use of a code.

    :param origin_lat: Origin coordinates.
    :param origin_lng: Origin coordinates.
    :param dest_lat: Destinatioh coordinates.
    :param dest_lng: Destinatioh coordinates.
    :param code: The code to use.
    :return: (<error code>, None) | Ok, {
        "code": <the code object used>,
        "polyline": <a polyline with origin and destination coordinates and
        several data about the code.>
    }
    """
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return RideFromPromCodeResult.PromCodeDoNotExists, None

    if not pcode.active:
        return RideFromPromCodeResult.PromCodeInactive, None

    if pcode.expired():
        return RideFromPromCodeResult.PromCodeExpired, None

    origin_valid = pcode.is_valid(origin_lat, origin_lng)
    dest_valid = pcode.is_valid(dest_lat, dest_lng)

    if not (origin_valid or dest_valid):
        return RideFromPromCodeResult.PromCodeInvalid, None

    cost = calculate_value(origin_lat, origin_lng, dest_lat, dest_lng)

    if pcode.credit < cost:
        return RideFromPromCodeResult.InsuficientCredit, None

    pcode.decrement_credit(cost)

    return RideFromPromCodeResult.Ok, {
        "code": pcode,
        "polyline": polyline.encode(
            [(origin_lat, origin_lng), (dest_lat, dest_lng)], 5),
    }
