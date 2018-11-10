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
from domain.models import Event, PromCode, db
from domain import prom_code

from domain.prom_code import GeneratePromoCodeResult, \
    PromoCodeResult, RideFromPromCodeResult, GeneratePromoCodeResult

import domain

from main import create_app


@pytest.fixture
def app():
    app = create_app(tconfig)
    app.debug = True
    return app


@pytest.fixture()
def models_data():
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


def test_promo_code_generation(models_data, mocker, app):
    """
    Generation of new promo codes for events
    """

    mock_code = "mock_code"

    template = "%d-%m-%Y"
    mock_time = datetime.datetime.strptime("01-02-2018", template)

    mocker.patch.object(domain.utils, 'string_generator', return_value=mock_code)
    mocker.patch.object(domain.utils, 'get_default_expiration_time', return_value=mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(10)
        assert response_code == GeneratePromoCodeResult.EventDoNotExists

        response_code, res = prom_code.generate_promo_code(1)
        event = Event.query.get(1)
        assert res.credit == tconfig.DEFAULT_CREDIT
        assert res.radius == event.radius
        assert res.code == mock_code
        assert res.expiration_time == mock_time


def test_promo_code_generation_expired(models_data, mocker, app):
    """

    """

    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("08-02-2018", template)
    default_expiration_time_mock_time = datetime.datetime.strptime("03-02-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)
    mocker.patch.object(domain.utils, 'get_default_expiration_time', return_value=default_expiration_time_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expired()


def test_promo_code_generation_notexpired(models_data, mocker, app):
    """

    """

    template = "%d-%m-%Y"
    default_expiration_mock_time = datetime.datetime.strptime("08-02-2018", template)
    now_mock_time = datetime.datetime.strptime("03-02-2018", template)

    mocker.patch.object(domain.utils, 'get_default_expiration_time', return_value=default_expiration_mock_time)

    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert not res.expired()


def test_promo_code_generation_default_expiration_time_length(models_data, mocker, app):
    """

    """

    template = "%d-%m-%Y"
    now_mock_time = datetime.datetime.strptime("01-02-2018", template)
    now_mock_time_plus_2_months = datetime.datetime.strptime("01-04-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=now_mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expiration_time < now_mock_time_plus_2_months


def test_promo_code_deactivation(models_data, mocker, app):
    """

    """

    mock_code = "mock_code"
    mocker.patch.object(domain.utils, 'string_generator', return_value=mock_code)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.active == True
        response_code, res = prom_code.deactivate_promo_code(mock_code)
        assert res.active == False
        response_code, res = prom_code.deactivate_promo_code(mock_code + mock_code)
        assert response_code == PromoCodeResult.PromoCodeDoNotExists


def test_promo_code_lists(models_data, mocker, app):
    """

    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code, pcode = prom_code.deactivate_promo_code(pcode.code)
        response_code, pcode2 = prom_code.generate_promo_code(1)
        response_code, pcode3 = prom_code.generate_promo_code(1)

        actives = prom_code.get_active_promo_codes(13)
        assert set([a.code for a in actives]) == set([])

        actives = prom_code.get_active_promo_codes(1)
        assert set([a.code for a in actives]) == set([pcode2.code, pcode3.code])

        all_codes = prom_code.get_all_promo_codes(1)
        assert set([a.code for a in all_codes]) == set([pcode2.code, pcode3.code, pcode.code])


def test_valid_promo_code_acording_distances(models_data, app):
    """

    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        assert pcode.is_valid(1.5, 1.1)
        assert not pcode.is_valid(1.5, 4.1)


def test_valid_promo_code_acording_distances_when_radius_change(models_data, app):
    """

    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        prom_code.set_radius_to_prom_code(pcode.code, 5000)
        assert pcode.is_valid(1.5, 4.1)


def test_promo_code_valid_acording_distances_radius_changed_using_event(models_data, mocker, app):
    """

    """

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        response_code, pcode2 = prom_code.generate_promo_code(1)
        response_code, pcode3 = prom_code.generate_promo_code(1)

        prom_code.set_radius_to_event(1, 5000)
        prom_code.spread_radius_from_event_to_all_prom_codes(1)

        assert pcode.is_valid(1.5, 4.1)
        assert pcode2.is_valid(1.5, 4.1)
        assert pcode3.is_valid(1.5, 4.1)


def test_ride_from_prom_code(models_data, mocker, app):
    """

    """

    mock_value = 2
    mocker.patch.object(domain.prom_code, 'calculate_value', return_value=mock_value)

    with app.app_context():
        response_code, pcode = prom_code.generate_promo_code(1)
        prom_code.deactivate_promo_code(pcode.code)
        response_code, pcode2 = prom_code.generate_promo_code(1)

        resp_code0, pcode3 = prom_code.get_ride_from_prom_code(1.5, 4.1, 5.3, 33.1, pcode.code)
        resp_code1, pcode4 = prom_code.get_ride_from_prom_code(11.5, 4.1, 5.3, 33.1, pcode2.code)
        resp_code2, pcode5 = prom_code.get_ride_from_prom_code(11.5, 4.1, 5.3, 33.1, pcode2.code + "1")

        credit = pcode2.credit

        resp_code3, pcode4 = prom_code.get_ride_from_prom_code(1.5, 1.3, 5.3, 33.1, pcode2.code)

        assert credit == pcode2.credit + mock_value

        assert resp_code0 == RideFromPromCodeResult.PromCodeInactive
        assert resp_code1 == RideFromPromCodeResult.PromCodeInvalid
        assert resp_code2 == RideFromPromCodeResult.PromCodeDoNotExists
        assert resp_code3 == RideFromPromCodeResult.Ok

