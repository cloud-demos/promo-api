from enum import Enum

import config
from domain.models import PromCode, Event, db
from domain import utils

GeneratePromoCodeResult = Enum('GeneratePromoCodeResult', 'EventDoNotExists Ok')


def generate_promo_code(event_id, data={}):

    pcode = PromCode()

    db.session.add(pcode)
    db.session.commit()

    return GeneratePromoCodeResult.Ok, pcode
