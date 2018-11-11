import os.path
import sys
import pytest
import datetime
from collections import namedtuple
from flask import url_for

curr_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(curr_dir, '../src')

sys.path.append(app_dir)

import tconfig

from domain import models
from domain.models import Event
from domain import prom_code

from domain.prom_code import GeneratePromoCodeResult, \
    PromoCodeResult, RideFromPromCodeResult, \
    SetRadiusFromEventsResult, SetRadiusResult

import domain

from main import create_app


@pytest.fixture
def app():
    """
    pytest flask plugin object
    """
    app = create_app(tconfig)
    app.debug = True
    return app


@pytest.fixture()
def models_data():
    """
    pytest fixture database object
    :return:
    """
    models.create_database(os.path.join(curr_dir, 'tconfig.py'))
    models.init_database_for_tests([
        {
            "fields": {
                "id": 1,
                "name": "Event 1",
                "lat": 1.4,
                "lng": 1.1,
                "radius": 50.0,
            },
            "model": "Event"
        },

    ], os.path.join(curr_dir, 'tconfig.py')
    )

    yield

    models.drop_database(os.path.join(curr_dir, 'tconfig.py'))


def test_promo_code_generation_default_values(models_data, mocker, app):
    """
    Generation of new promo codes using default values
    """
    mock_code = "mock_code"

    template = "%d-%m-%Y"
    mock_time = datetime.datetime.strptime("01-02-2018", template)

    mocker.patch.object(domain.utils, 'string_generator',
                        return_value=mock_code)
    mocker.patch.object(domain.utils, 'get_default_expiration_time',
                        return_value=mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(10)
        assert response_code == GeneratePromoCodeResult.EventDoNotExists

        response_code, res = prom_code.generate_promo_code(1)
        event = Event.query.get(1)
        assert res.credit == tconfig.DEFAULT_CREDIT
        assert res.radius == event.radius
        assert res.code == mock_code
        assert res.expiration_time == mock_time


def test_promo_code_generation(models_data, mocker, app):
    """
    Generation of new promo codes for events
    """

    mock_code = "mock_code"
    CREDIT = 23
    radius = 99

    template = "%m-%d-%Y"
    mock_time = datetime.datetime.strptime("01-02-2018", template)

    mocker.patch.object(domain.utils, 'string_generator',
                        return_value=mock_code)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(10)
        assert response_code == GeneratePromoCodeResult.EventDoNotExists
        event_id = 1
        response_code, res = prom_code.generate_promo_code(event_id, {
            "credit": CREDIT,
            "radius": radius,
            "event_id": event_id,
            "expiration_time": datetime.datetime.strftime(mock_time, template),
        })
        assert res.credit == CREDIT
        assert res.radius == radius
        assert res.code == mock_code
        assert res.event_id == event_id
        assert res.expiration_time == mock_time


def test_promo_code_generation_expired(models_data, mocker, app):
    """
        The promo code can expire
    """

    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("08-02-2018", template)
    default_expiration_time_mock_time = datetime.datetime.strptime(
        "03-02-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)
    mocker.patch.object(domain.utils, 'get_default_expiration_time',
                        return_value=default_expiration_time_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expired()


def test_promo_code_generation_notexpired(models_data, mocker, app):
    template = "%d-%m-%Y"
    default_expiration_mock_time = datetime.datetime.strptime(
        "08-02-2018", template)
    now_mock_time = datetime.datetime.strptime("03-02-2018", template)

    mocker.patch.object(domain.utils, 'get_default_expiration_time',
                        return_value=default_expiration_mock_time)

    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert not res.expired()


def test_promo_code_generation_default_expiration_time_length(models_data,
                                                              mocker, app):
    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("01-02-2018", template)
    now_mock_time_plus_2_months = datetime.datetime.strptime(
        "01-04-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expiration_time < now_mock_time_plus_2_months


def test_promo_code_deactivation_activation(models_data, mocker, app):
    """
        The promo code can be deactivated
    """

    mock_code = "mock_code"
    mocker.patch.object(domain.utils, 'string_generator',
                        return_value=mock_code)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.active == True

        response_code, res = prom_code.deactivate_promo_code(mock_code)
        assert res.active == False

        response_code, res = prom_code.activate_promo_code(mock_code)
        assert res.active == True

        response_code, res = prom_code.deactivate_promo_code(
            mock_code + mock_code)
        assert response_code == PromoCodeResult.PromoCodeDoNotExists

        response_code, res = prom_code.activate_promo_code(
            mock_code + mock_code)
        assert response_code == PromoCodeResult.PromoCodeDoNotExists


def test_promo_code_lists(models_data, mocker, app):
    """
        Return all promo codes
    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code, pcode = prom_code.deactivate_promo_code(pcode.code)
        response_code, pcode2 = prom_code.generate_promo_code(1)
        response_code, pcode3 = prom_code.generate_promo_code(1)

        actives = prom_code.get_active_promo_codes(13)
        assert set([a.code for a in actives]) == set([])

        actives = prom_code.get_active_promo_codes(1)
        assert set([a.code for a in actives]) == set([pcode2.code, pcode3.code]
                                                     )

        all_codes = prom_code.get_all_promo_codes(1)
        assert set([a.code for a in all_codes]) == set([pcode2.code,
                                                        pcode3.code, pcode.code
                                                        ]
                                                       )


def test_valid_promo_code_acording_distances(models_data, app):
    """
        Only valid when user’s pickup or destination is within x radius of the
        event venue
    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        assert pcode.is_valid(1.5, 1.1)
        assert not pcode.is_valid(1.5, 4.1)


def test_valid_promo_code_acording_distances_when_radius_change(models_data,
                                                                app):
    """
        Only valid when user’s pickup or destination is within x radius of the
        event venue
    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        prom_code.set_radius_to_prom_code(pcode.code, 5000)
        assert pcode.is_valid(1.5, 4.1)


def test_radius_change(models_data, app):
    """
        Only valid when user’s pickup or destination is within x radius of the
        event venue
    """

    with app.app_context():
        response_code, pcode = prom_code.set_radius_to_prom_code("code", 3)
        assert response_code == SetRadiusResult.PromCodeDoNotExists


def test_promo_code_valid_acording_distances_radius_changed_using_event(
        models_data, mocker, app):
    """
        Only valid when user’s pickup or destination is within x radius of the
        event venue
    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code, pcode2 = prom_code.generate_promo_code(1)
        response_code, pcode3 = prom_code.generate_promo_code(1)

        prom_code.set_radius_to_event(1, 5000)

        response_code, pcode4 = prom_code.set_radius_to_event(11, 5000)

        assert response_code == SetRadiusFromEventsResult.EventDoNotExists

        prom_code.spread_radius_from_event_to_all_prom_codes(1)

        assert response_code == SetRadiusFromEventsResult.EventDoNotExists

        response_code, pcode5 = prom_code. \
            spread_radius_from_event_to_all_prom_codes(11)

        assert response_code == SetRadiusFromEventsResult.EventDoNotExists

        assert pcode.is_valid(1.5, 4.1)
        assert pcode2.is_valid(1.5, 4.1)
        assert pcode3.is_valid(1.5, 4.1)


def test_ride_from_prom_code(models_data, mocker, app):
    """
        To test the validity of the promo code, expose an endpoint that accept
        origin, destination, the promo code. The api should return the promo
        code details and a polyline using the destination and origin if promo
        code is valid and an error otherwise.
    """

    mock_value = 2
    mocker.patch.object(domain.prom_code, 'calculate_value',
                        return_value=mock_value)

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        prom_code.deactivate_promo_code(pcode.code)
        response_code, pcode2 = prom_code.generate_promo_code(1)

        resp_code0, pcode3 = prom_code.get_ride_from_prom_code(
            1.5, 4.1, 5.3, 33.1, pcode.code)
        resp_code1, pcode4 = prom_code.get_ride_from_prom_code(
            11.5, 4.1, 5.3, 33.1, pcode2.code)
        resp_code2, pcode5 = prom_code.get_ride_from_prom_code(
            11.5, 4.1, 5.3, 33.1, pcode2.code + "1")

        credit = pcode2.credit

        resp_code3, pcode4 = prom_code.get_ride_from_prom_code(
            1.5, 1.3, 5.3, 33.1, pcode2.code)

        response_code, pcode5 = prom_code.generate_promo_code(1)
        pcode5.decrement_credit(pcode5.credit - 1)
        resp_code4, pcode5 = prom_code.get_ride_from_prom_code(
            1.5, 1.3, 44.3, 88.1, pcode5.code)

        assert credit == pcode2.credit + mock_value

        assert resp_code0 == RideFromPromCodeResult.PromCodeInactive
        assert resp_code1 == RideFromPromCodeResult.PromCodeInvalid
        assert resp_code2 == RideFromPromCodeResult.PromCodeDoNotExists
        assert resp_code3 == RideFromPromCodeResult.Ok
        assert resp_code4 == RideFromPromCodeResult.InsuficientCredit


def test_ride_from_prom_code_expired_error(models_data, mocker, app):
    """
        To test the validity of the promo code, expose an endpoint that accept
        origin, destination, the promo code. The api should return the promo
        code details and a polyline using the destination and origin if promo
        code is valid and an error otherwise.

        Case: code expired
    """

    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("08-02-2018", template)
    default_expiration_time_mock_time = datetime.datetime.strptime(
        "03-02-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)
    mocker.patch.object(domain.utils, 'get_default_expiration_time',
                        return_value=default_expiration_time_mock_time)

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code2, pcode2 = prom_code.get_ride_from_prom_code(
            1.5, 4.1, 5.3, 33.1, pcode.code)
        assert response_code2 == RideFromPromCodeResult.PromCodeExpired


def test_prom_code_expired_error(models_data, mocker, app):
    """
        To test the validity of the promo code, expose an endpoint that accept
        origin, destination, the promo code. The api should return the promo
        code details and a polyline using the destination and origin if promo
        code is valid and an error otherwise.

        Case: code expired error (EventDoNotExists)

    """

    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("08-02-2018", template)
    default_expiration_time_mock_time = datetime.datetime.strptime(
        "03-02-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)
    mocker.patch.object(domain.utils, 'get_default_expiration_time',
                        return_value=default_expiration_time_mock_time)

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code2, result = prom_code.promo_code_is_expired(pcode.code)
        response_code3, result2 = prom_code.promo_code_is_expired(
            pcode.code + pcode.code)
        assert response_code2 == PromoCodeResult.Ok
        assert result == True
        assert response_code3 == PromoCodeResult.PromoCodeDoNotExists


def test_flask_prom_code_generate_error(models_data, mocker, client, app):
    """
        Generation of new promo codes for events

        Case: error when the event do not exists
    """
    mock_response = GeneratePromoCodeResult.EventDoNotExists, None
    mocker.patch.object(domain.prom_code, 'generate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.prom_code_generate'),
                          json={
                              "expiration_time": "02-01-2018",
                              "event_id": 1,
                          })
        assert res.json["status"] == "error"


def test_flask_prom_code_generate_ok(models_data, mocker, client, app):
    """
        Generation of new promo codes for events
    """
    PromoCodeResultTuple = namedtuple('PromoCodeResultTuple', 'code')
    mock_code = "mock_code"
    mock_response = GeneratePromoCodeResult.Ok, PromoCodeResultTuple(mock_code)
    mocker.patch.object(domain.prom_code, 'generate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.prom_code_generate'),
                          json={
                              "expiration_time": "02-01-2018",
                              "event_id": 1,
                          })
        assert res.json["code"] == mock_code


def test_flask_prom_code_generate_400_error(models_data, mocker, client, app):
    """
        Generation of new promo codes for events

        Case: error when the event_id is missing
    """
    with app.app_context():
        res = client.post(url_for('codes.prom_code_generate'),
                          json={
                              "expiration_time": "02-01-2018",
                          })
        assert res.status_code == 400


def test_flask_is_expired_promo_code_error(models_data, mocker, client, app):
    """
        Endpoint to query the expiration of a code

        Case: error when the code do not exists
    """
    mock_response = PromoCodeResult.PromoCodeDoNotExists, None
    mocker.patch.object(domain.prom_code, 'promo_code_is_expired',
                        return_value=mock_response)

    with app.app_context():
        res = client.get(f"{url_for('codes.prom_code_expired')}?"
                         f"code=mock_code")

        assert res.json["status"] == "error"


def test_flask_is_expired_promo_code_ok(models_data, mocker, client, app):
    """
        Endpoint to query the expiration of a code
    """
    mock_response = PromoCodeResult.Ok, True
    mocker.patch.object(domain.prom_code, 'promo_code_is_expired',
                        return_value=mock_response)

    with app.app_context():
        res = client.get(f"{url_for('codes.prom_code_expired')}?"
                         f"code=mock_code")

        assert res.json["status"] == "ok"
        assert res.json["expired"] == True


def test_flask_promo_code_list(models_data, mocker, client, app):
    """
        Return all promo codes

        Endpoint to query all the codes
    """
    mock_response = [1, 2, 4, 1]
    mocker.patch.object(domain.prom_code, 'get_all_promo_codes',
                        return_value=mock_response)

    with app.app_context():
        res = client.get(f"{url_for('codes.prom_code_list')}?"
                         f"page=2&event_id=1")

        assert len(res.json) == 4


def test_flask_promo_code_list_active(models_data, mocker, client, app):
    """
        Return active promo codes

        Endpoint to query all the active codes
    """
    mock_response = [1, 2, 4, 1]
    mocker.patch.object(domain.prom_code, 'get_active_promo_codes',
                        return_value=mock_response)

    with app.app_context():
        res = client.get(f"{url_for('codes.prom_code_active_list')}?page=2&"
                         f"event_id=1")

        assert len(res.json) == 4


def test_flask_promo_code_activate_error(models_data, mocker, client, app):
    """
        Code activation

        Case: error, when the code do not exists
    """
    mock_response = PromoCodeResult.PromoCodeDoNotExists, None
    mocker.patch.object(domain.prom_code, 'activate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.put(f"{url_for('codes.prom_code_activation')}?"
                         f"code=mock_code")

        assert res.json["status"] == "error"


def test_flask_promo_code_activate_400_error(models_data, mocker, client, app):
    """
        Code activation

        Case: error, when the code value is missing
    """
    with app.app_context():
        res = client.put(url_for('codes.prom_code_activation'))
        assert res.status_code == 400


def test_flask_promo_code_activate_ok(models_data, mocker, client, app):
    """
        Code activation

        Case: ok
    """
    PromoCodeResultTuple = namedtuple('PromoCodeResultTuple', 'code')
    mock_code = "mock_code"
    mock_response = PromoCodeResult.Ok, PromoCodeResultTuple(mock_code)
    mocker.patch.object(domain.prom_code, 'activate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.put(f"{url_for('codes.prom_code_activation')}?"
                         f"code=mock_code")
        assert res.json["code"] == mock_code


def test_flask_promo_code_deactivate_error(models_data, mocker, client, app):
    """
        Codes can be deactivated

        Case: error, when the code do not exists
    """
    mock_response = PromoCodeResult.PromoCodeDoNotExists, None
    mocker.patch.object(domain.prom_code, 'deactivate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.put(f"{url_for('codes.prom_code_deactivation')}?"
                         f"code=mock_code")

        assert res.json["status"] == "error"


def test_flask_promo_code_deactivate_ok(models_data, mocker, client, app):
    """
        Codes can be deactivated

        Case: ok
    """
    PromoCodeResultTuple = namedtuple('PromoCodeResultTuple', 'code')
    mock_code = "mock_code"
    mock_response = PromoCodeResult.Ok, PromoCodeResultTuple(mock_code)
    mocker.patch.object(domain.prom_code, 'deactivate_promo_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.put(f"{url_for('codes.prom_code_deactivation')}?"
                         f"code=mock_code")
        assert res.json["code"] == mock_code


def test_flask_set_radius_to_event_error(models_data, mocker, client, app):
    """
        To change the radius to an event

        Case: error, when the event do not exists
    """
    mock_response = SetRadiusFromEventsResult.EventDoNotExists, None
    mocker.patch.object(domain.prom_code, 'set_radius_to_event',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.set_radius_to_event'),
                          json={
                              "radius": 12.8,
                              "event_id": 1,
                          })

        assert res.json["status"] == "error"


def test_flask_set_radius_to_event_error_400(models_data, mocker, client, app):
    """
        To change the radius to an event

        Case: error, when a required field is missing the framework returns a
        400 error
    """
    with app.app_context():
        res = client.post(url_for('codes.set_radius_to_event'),
                          json={
                              "event_id": 1,
                          })
        assert res.status_code == 400


def test_flask_set_radius_to_event_ok(models_data, mocker, client, app):
    """
        To change the radius to an event

        Case: ok
    """
    EventResultTuple = namedtuple('EventResultTuple', 'name')
    mock_name = "mock_name"
    mock_response = SetRadiusFromEventsResult.Ok, EventResultTuple(mock_name)
    mocker.patch.object(domain.prom_code, 'set_radius_to_event',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.set_radius_to_event'),
                          json={
                              "radius": 12.8,
                              "event_id": 1,
                          })
        assert res.json["event_name"] == mock_name


def test_flask_spread_radius_from_event_to_all_prom_codes_error(
        models_data, mocker, client, app):
    """
        To change the radius to all the codes of an specific event

        Case: error, the event do not exists
    """
    mock_response = SetRadiusFromEventsResult.EventDoNotExists, None
    mocker.patch.object(domain.prom_code,
                        'spread_radius_from_event_to_all_prom_codes',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.spread_radius_in_event'),
                          json={
                              "event_id": 1,
                          })

        assert res.json["status"] == "error"


def test_flask_spread_radius_from_event_to_all_prom_codes_ok(
        models_data, mocker, client, app):
    """
        To change the radius to an event

        Case: ok
    """
    EventResultTuple = namedtuple('EventResultTuple', 'name')
    mock_name = "mock_name"
    mock_response = SetRadiusFromEventsResult.Ok, EventResultTuple(mock_name)
    mocker.patch.object(
        domain.prom_code, 'spread_radius_from_event_to_all_prom_codes',
        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.spread_radius_in_event'),
                          json={
                              "event_id": 1,
                          })

        assert res.json["event_name"] == mock_name


def test_flask_set_radius_to_prom_code_error(models_data, mocker, client, app):
    """
        To change the radius to a code

        Case: error, when the code do not exists
    """
    mock_response = SetRadiusResult.PromCodeDoNotExists, None
    mocker.patch.object(domain.prom_code, 'set_radius_to_prom_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.set_radius_to_prom_code'),
                          json={
                              "code": "mock_code",
                              "radius": 10.2,
                          })

        assert res.json["status"] == "error"


def test_flask_set_radius_to_prom_code_ok(models_data, mocker, client, app):
    """
        To change the radius to an event

        Case: ok
    """
    PromoCodeResultTuple = namedtuple('PromoCodeResultTuple', 'code')
    mock_code = "mock_code"
    mock_response = SetRadiusResult.Ok, PromoCodeResultTuple(mock_code)
    mocker.patch.object(domain.prom_code, 'set_radius_to_prom_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.set_radius_to_prom_code'),
                          json={
                              "code": "code",
                              "radius": 10.2,
                          })

        assert res.json["code"] == mock_code


def get_ride_from_prom_code_error(
        models_data, mocker, client, app, mock_response_code):
    """
        To test the validity of the promo code, expose an endpoint that accept
        origin, destination, the promo code. The api should return the promo
        code details and a polyline using the destination and origin if promo
        code is valid and an error otherwise.

        Case: error, when a requirement is not satisfied
    """
    mock_response = mock_response_code, None
    mocker.patch.object(domain.prom_code, 'get_ride_from_prom_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.get_ride_from_prom_code'),
                          json={
                              "code": "mock_code",
                              "origin_lat": 10.2,
                              "origin_lng": 10.2,
                              "dest_lat": 10.2,
                              "dest_lng": 10.2,
                          })

        assert res.json["status"] == "error"


def test_flask_get_ride_from_prom_code_PromCodeDoNotExists_error(
        models_data, mocker, client, app):
    get_ride_from_prom_code_error(models_data,
                                  mocker,
                                  client,
                                  app,
                                  RideFromPromCodeResult.PromCodeDoNotExists)


def test_flask_get_ride_from_prom_code_PromCodeInactive_error(
        models_data, mocker, client, app):
    get_ride_from_prom_code_error(models_data,
                                  mocker,
                                  client,
                                  app,
                                  RideFromPromCodeResult.PromCodeInactive)


def test_flask_get_ride_from_prom_code_PromCodeInvalid_error(
        models_data, mocker, client, app):
    get_ride_from_prom_code_error(models_data,
                                  mocker,
                                  client,
                                  app,
                                  RideFromPromCodeResult.PromCodeInvalid)


def test_flask_get_ride_from_prom_code_InsuficientCredit_error(
        models_data, mocker, client, app):
    get_ride_from_prom_code_error(models_data,
                                  mocker,
                                  client,
                                  app,
                                  RideFromPromCodeResult.InsuficientCredit)


def test_flask_get_ride_from_prom_code_PromCodeExpired_error(
        models_data, mocker, client, app):
    get_ride_from_prom_code_error(models_data,
                                  mocker,
                                  client,
                                  app,
                                  RideFromPromCodeResult.PromCodeExpired)


def test_flask_get_ride_from_prom_code_ok(models_data, mocker, client, app):
    RideFromPromCodeResultTuple = namedtuple('RideFromPromCodeResultTuple',
                                             'code credit event_id '
                                             'expiration_time ')
    """
        To test the validity of the promo code, expose an endpoint that accept 
        origin, destination, the promo code. The api should return the promo 
        code details and a polyline using the destination and origin if promo 
        code is valid and an error otherwise. 

        Case: ok
    """
    mock_code = "mock_code"
    mock_credit = 34
    mock_event_id = 3
    template = "%d-%m-%Y"
    mock_expiration_time = datetime.datetime.strptime("01-02-2018", template)
    mock_response = RideFromPromCodeResult.Ok, {
        "code": RideFromPromCodeResultTuple(
            mock_code, mock_credit, mock_event_id,
            mock_expiration_time
        ),
        "polyline": "polyline",
    }
    mocker.patch.object(domain.prom_code, 'get_ride_from_prom_code',
                        return_value=mock_response)

    with app.app_context():
        res = client.post(url_for('codes.get_ride_from_prom_code'),
                          json={
                              "code": "mock_code",
                              "origin_lat": 10.2,
                              "origin_lng": 10.2,
                              "dest_lat": 10.2,
                              "dest_lng": 10.2,
                          })

        assert res.json["status"] == "ok"
        assert res.json["code"] == mock_code
        assert res.json["event_id"] == mock_event_id
