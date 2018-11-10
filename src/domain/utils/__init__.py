import string
import random

import dateutil.relativedelta
import datetime
import config


def get_now():
    return datetime.datetime.now()


def get_default_expiration_time():
    now = get_now()
    default_expiration_time = now + dateutil.relativedelta.relativedelta(
        years=config.Expiration_time_Years,
        months=config.Expiration_time_Months,
        days=config.Expiration_time_Days,
    )
    return default_expiration_time


def string_generator(size=8, chars=string.ascii_letters + string.digits):
    """
    size: default=8; override to provide smaller/larger passwords.

    chars: default=A-Za-z0-9; override to provide more/less diversity

    Credit: Ignacio Vasquez-Abrams
    Source: http://stackoverflow.com/a/2257449
    .
    """
    return ''.join(random.choice(chars) for _ in range(size))
