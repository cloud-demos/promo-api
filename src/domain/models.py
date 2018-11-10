"""Docs."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from geopy import distance

import domain.utils as utils

import json
import datetime
import argparse

builtin_list = list

db = SQLAlchemy()


def init_app(app_to_init):
    """Docs."""
    db.init_app(app_to_init)


class Event(db.Model):
    """Docs."""

    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    name = db.Column(db.String(50))
    radius = db.Column(db.Float)  # in miles

    prom_codes = db.relationship('PromCode', backref='event',
                                 lazy='dynamic')

    def set_radius(self, radius):
        self.radius = radius
        db.session.commit()


class PromCode(db.Model):
    """Docs."""

    __tablename__ = 'prom_codes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    credit = db.Column(db.Float)
    code = db.Column(db.String(20), primary_key=True)
    radius = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    creation_time = db.Column(db.DateTime, nullable=False,
                              default=datetime.datetime.now)
    expiration_time = db.Column(db.DateTime, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)

    def expired(self):
        now = utils.get_now()
        return self.expiration_time < now

    def deactivate(self):
        self.active = False
        db.session.commit()

    def activate(self):
        self.active = True
        db.session.commit()

    def is_valid(self, lat, lng):
        return self.radius >= distance.distance(
            (self.event.lat, self.event.lng), (lat, lng)).miles

    def set_radius(self, radius):
        self.radius = radius
        db.session.commit()

    def decrement_credit(self, cost):
        self.credit -= cost
        db.session.commit()


def create_database(config_file='../config.py'):
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    temp_app = Flask(__name__)
    temp_app.config.from_pyfile(config_file)
    init_app(temp_app)
    with temp_app.app_context():
        db.create_all()
    print("All tables created")


def drop_database(config_file='../config.py'):
    """Docs."""
    temp_app = Flask(__name__)
    temp_app.config.from_pyfile(config_file)
    init_app(temp_app)
    with temp_app.app_context():
        db.drop_all()

    print("All tables deleted")


def _mk_objects(d):
    for v in d:
        # print(v)
        m = v['model']
        ModelClass = eval(m)
        fields = v['fields']
        if 'ForeignKeys' in v:
            foreign_keys = v['ForeignKeys']
            res = []
            for field, fkClass in foreign_keys:
                rel = fields[field]
                del fields[field]
                res.append([field, fkClass, rel])

        a = ModelClass(**fields)
        if 'ForeignKeys' in v:
            for field, fkClass, rel in res:
                FK = eval(fkClass)
                for r in rel:
                    p = FK.query.get(r)
                    eval('a.' + field + '.append(p)')

        db.session.add(a)


def init_database(config_file='../config.py'):
    """Docs."""
    temp_app = Flask(__name__)
    temp_app.config.from_pyfile(config_file)

    init_datas = [json.loads(open('src/domain/fixtures/initial-data.json')
                             .read())]

    if temp_app.config["LOCAL"]:
        init_datas.append(json.loads(open(
            'src/domain/fixtures/local-data.json').read()))

    init_database_common(temp_app, init_datas)


def init_database_for_tests(init_datas, config_file='../config.py'):
    """Docs."""
    temp_app = Flask(__name__)
    temp_app.config.from_pyfile(config_file)

    init_database_common(temp_app, [init_datas])


def init_database_common(temp_app, init_datas):
    """Docs."""
    init_app(temp_app)
    with temp_app.app_context():
        for data in init_datas:
            _mk_objects(data)
        db.session.commit()
    print("Tables initialized")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Database utilities')

    parser.add_argument(
        '-a', '--action', type=str, default='init',
        help='Options: init (fill tables whit initial data, the default), '
             'd (delete)')

    args = parser.parse_args()

    if args.action == "d" or args.action == "delete":

        # litle hack to delete alembic table!
        class AlembicVersion(db.Model):
            """Docs."""

            __tablename__ = 'alembic_version'
            version_num = db.Column(db.String(32), primary_key=True)


        drop_database()
    else:
        # create_database()
        # init_database()
        pass
