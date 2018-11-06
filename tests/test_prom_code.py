import os.path
import sys
import pytest

curr_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(curr_dir, '../src')

sys.path.append(app_dir)

import tconfig

from domain import models


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


def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(tconfig)
    models.db.init_app(app)
    return app


def test_event(models_data):
    app = create_app()
    from domain import prom_code
    with app.app_context():
        event = models.Event.query.get(1)
        assert event.name == "Event 1"

