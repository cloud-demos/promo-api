from enum import Enum

import config
from domain.models import PromCode, Event, db
from domain import utils

GeneratePromoCodeResult = Enum('GeneratePromoCodeResult', 'EventDoNotExists Ok')


def generate_promo_code(event_id, data={}):
    event = Event.query.get(event_id)
    if not event:
        return GeneratePromoCodeResult.EventDoNotExists, None

    pcode = PromCode(
        credit=data.get("credit", config.DEFAULT_CREDIT),
        radius=data.get("radius", config.DEFAULT_RADIUS),
        expiration_time=data.get("expiration_time", utils.get_default_expiration_time()),
        code=utils.string_generator(config.CODE_LENGTH),
    )

    db.session.add(pcode)
    db.session.commit()

    return GeneratePromoCodeResult.Ok, pcode
