import graphene
from . import code_generation
from . import get_ride
from . import state
from . import radius


class MyMutations(graphene.ObjectType):
    create_codes = code_generation.CreateCodes.Field()
    get_ride = get_ride.GetRideFromPromoCode.Field()
    state = state.StateCode.Field()
    radius_to_event = radius.SetRadiusToEvent.Field()
    radius_to_code = radius.SetRadiusToPromCode.Field()
    spread_radius_in_event = radius.SpreadRadiusToEvent.Field()
