from flask import Blueprint
from flask_restplus import Api

prom_code_blue_print = Blueprint('codes', __name__)

api = Api(prom_code_blue_print, doc="/swagger")

from . import list_codes
from . import generate_promo
from . import promo_code_activation_expiration
from . import radius_seter
from . import get_ride_from_code

