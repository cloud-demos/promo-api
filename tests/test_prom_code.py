import os.path
import sys
import pytest
import datetime

curr_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(curr_dir, '../src')

sys.path.append(app_dir)

import tconfig

from domain import models
from domain import prom_code

from domain.prom_code import GeneratePromoCodeResult
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
        assert res.credit == tconfig.DEFAULT_CREDIT
        assert res.radius == tconfig.DEFAULT_RADIUS
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

