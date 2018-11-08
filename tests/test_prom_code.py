import os.path
import sys
import pytest
import datetime

curr_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(curr_dir, '../src')

sys.path.append(app_dir)

import tconfig

from domain import models
from domain.models import Event, PromCode, db
from domain import prom_code

from domain.prom_code import GeneratePromoCodeResult, DeactivatePromoCodeResult
import domain


def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(tconfig)
    models.db.init_app(app)
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


def test_promo_code_generation(models_data, mocker):
    """
    Generation of new promo codes for events
    """
    app = create_app()

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


def test_promo_code_generation3(models_data, mocker):
    """

    """
    app = create_app()

    template = "%d-%m-%Y"
    mock_time = datetime.datetime.strptime("08-02-2018", template)
    mock_time2 = datetime.datetime.strptime("03-02-2018", template)
    mocker.patch.object(domain.utils, 'get_default_expiration_time', return_value=mock_time2)
    mocker.patch.object(domain.utils, 'get_now', return_value=mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expired()


def test_promo_code_generation4(models_data, mocker):
    """

    """
    app = create_app()

    template = "%d-%m-%Y"
    mock_time = datetime.datetime.strptime("08-02-2018", template)
    mock_time2 = datetime.datetime.strptime("03-02-2018", template)

    mocker.patch.object(domain.utils, 'get_default_expiration_time', return_value=mock_time)

    mocker.patch.object(domain.utils, 'get_now', return_value=mock_time2)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert not res.expired()


def test_promo_code_generation2(models_data, mocker):
    """

    """
    app = create_app()

    template = "%d-%m-%Y"
    mock_time = datetime.datetime.strptime("01-02-2018", template)
    mock_time_plus_2_months = datetime.datetime.strptime("01-04-2018", template)
    mocker.patch.object(domain.utils, 'get_now', return_value=mock_time)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.expiration_time < mock_time_plus_2_months


def test_promo_code_deactivation(models_data, mocker):
    """

    """
    app = create_app()
    mock_code = "mock_code"
    mocker.patch.object(domain.utils, 'string_generator', return_value=mock_code)

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.active == True
        response_code, res = prom_code.deactivate_promo_code(mock_code)
        assert res.active == False
        response_code, res = prom_code.deactivate_promo_code(mock_code + mock_code)
        assert response_code == DeactivatePromoCodeResult.PromoCodeDoNotExists


def test_promo_code_lists(models_data, mocker):
    """

    """
    app = create_app()

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        response_code, res = prom_code.deactivate_promo_code(res.code)
        response_code, res2 = prom_code.generate_promo_code(1)
        response_code, res3 = prom_code.generate_promo_code(1)

        actives = prom_code.get_active_promo_codes(13)
        assert set([a.code for a in actives]) == set([])

        actives = prom_code.get_active_promo_codes(1)
        assert set([a.code for a in actives]) == set([res2.code, res3.code])

        all_codes = prom_code.get_all_promo_codes(1)
        assert set([a.code for a in all_codes]) == set([res2.code, res3.code, res.code])


def test_promo_code_valid_acording_distances(models_data):
    """

    """
    app = create_app()

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        assert res.is_valid(1.5, 1.1)
        assert not res.is_valid(1.5, 4.1)


def test_promo_code_valid_acording_distances_radius_changed(models_data):
    """

    """
    app = create_app()

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        prom_code.set_radius_to_prom_code(res.code, 5000)
        assert res.is_valid(1.5, 4.1)


def test_promo_code_valid_acording_distances_radius_changed_using_event(models_data, mocker):
    """

    """
    app = create_app()

    with app.app_context():
        response_code, res = prom_code.generate_promo_code(1)
        response_code, res2 = prom_code.generate_promo_code(1)
        response_code, res3 = prom_code.generate_promo_code(1)

        prom_code.set_radius_to_event(1, 5000)
        prom_code.spread_radius_from_event_to_all_prom_codes(1)

        assert res.is_valid(1.5, 4.1)
        assert res2.is_valid(1.5, 4.1)
        assert res3.is_valid(1.5, 4.1)

