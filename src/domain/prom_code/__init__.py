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

    pcode = PromCode(
        event_id=event_id,
        credit=data.get("credit", config.DEFAULT_CREDIT),
        radius=data.get("radius", config.DEFAULT_RADIUS),
        expiration_time=data.get("expiration_time", utils.get_default_expiration_time()),
        code=utils.string_generator(config.CODE_LENGTH),
    )

    db.session.add(pcode)
    db.session.commit()

    return GeneratePromoCodeResult.Ok, pcode


DeactivatePromoCodeResult = Enum('DeactivatePromoCodeResult', 'PromoCodeDoNotExists Ok')


def deactivate_promo_code(code):
    pcode = db.session.query(PromCode).filter(PromCode.code == code).first()
    if not pcode:
        return DeactivatePromoCodeResult.PromoCodeDoNotExists, None

    pcode.deactivate()

    return DeactivatePromoCodeResult.Ok, pcode


def get_all_promo_codes(event_id):
    # todo: add pagination
    return db.session.query(PromCode).filter(
        PromCode.event_id == event_id)


def get_active_promo_codes(event_id):
    # todo: add pagination
    return db.session.query(PromCode).filter(
        and_(PromCode.active, PromCode.event_id == event_id))
