from enum import Enum

import config
from domain.models import PromCode, Event, db
from domain import utils

from sqlalchemy import and_

GeneratePromoCodeResult = Enum('GeneratePromoCodeResult', 'EventDoNotExists Ok')


def generate_promo_code(event_id, data={}):
    event = Event.query.get(event_id)
    if not event:
        return GeneratePromoCodeResult.EventDoNotExists, None

    pcode = True
    while pcode:
        code = utils.string_generator(config.CODE_LENGTH)
        pcode = db.session.query(PromCode).filter(PromCode.code == code).first()

    pcode = PromCode(
        event_id=event_id,
        credit=data.get("credit", config.DEFAULT_CREDIT),
        radius=data.get("radius", event.radius),
        expiration_time=data.get("expiration_time", utils.get_default_expiration_time()),
        code=code,
    )

    db.session.add(pcode)
    db.session.commit()

    return GeneratePromoCodeResult.Ok, pcode


PromoCodeResult = Enum('PromoCodeResult', 'PromoCodeDoNotExists Ok')


def deactivate_promo_code(code):
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return PromoCodeResult.PromoCodeDoNotExists, None

    pcode.deactivate()

    return PromoCodeResult.Ok, pcode


def activate_promo_code(code):
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return PromoCodeResult.PromoCodeDoNotExists, None

    pcode.activate()

    return PromoCodeResult.Ok, pcode


def get_all_promo_codes(event_id, page=1, page_length=50):
    offset = (page - 1) * page_length
    return db.session.query(PromCode).filter(
        PromCode.event_id == event_id).offset(offset).limit(page_length).all()


def get_active_promo_codes(event_id, page=1, page_length=50):
    offset = (page - 1) * page_length
    return db.session.query(PromCode).filter(
        and_(PromCode.active, PromCode.event_id == event_id)).offset(offset).limit(page_length).all()


SetRadiusFromEventsResult = Enum('SetRadiusFromEventsResult', 'EventDoNotExists Ok')


def set_radius_to_event(event_id, radius):
    event = Event.query.get(event_id)
    if not event:
        return SetRadiusFromEventsResult.EventDoNotExists, None

    event.set_radius(radius)
    return SetRadiusFromEventsResult.Ok, event


def spread_radius_from_event_to_all_prom_codes(event_id):
    event = Event.query.get(event_id)
    if not event:
        return SetRadiusFromEventsResult.EventDoNotExists, None

    for pcode in event.prom_codes:
        pcode.set_radius(event.radius)

    return SetRadiusFromEventsResult.Ok, event


SetRadiusResult = Enum('SetRadiusResult', 'PromCodeDoNotExists Ok')


def set_radius_to_prom_code(code, radius):
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return SetRadiusResult.PromCodeDoNotExists, None
    pcode.set_radius(radius)
    return SetRadiusResult.Ok, pcode


RideFromPromCodeResult = Enum('RideFromPromCodeResult', 'PromCodeDoNotExists PromCodeInactive PromCodeInvalid InsuficientCredit Ok')

import polyline
from geopy import distance


def calculate_value(origin_lat, origin_lng, dest_lat, dest_lng):
    dist = distance.distance((origin_lat, origin_lng), (dest_lat, dest_lng)).miles
    return dist * config.MILES_COST


def get_ride_from_prom_code(origin_lat, origin_lng, dest_lat, dest_lng, code):
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return RideFromPromCodeResult.PromCodeDoNotExists, None

    if not pcode.active:
        return RideFromPromCodeResult.PromCodeInactive, None

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
        "polyline": polyline.encode([(origin_lat, origin_lng), (dest_lat, dest_lng)], 5),
    }
