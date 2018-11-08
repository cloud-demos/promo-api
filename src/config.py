import os

import logging

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", 'ERROR')

eval(f'logging.basicConfig(level=logging.{LOGGING_LEVEL})')

# SERVER_PREFIX = "http://localhost:8080"
SERVER_PREFIX = "https://dev.app.safeboda.io"

JWT_SECRET = 'bmiznfu5bghP/C/aM4tQtV7M+HV16rOLulIjTypGlWnHPZze9+LB3u86hFaA2hlb+W/bvIYlpXw3'

SECRET_KEY = '5eBLvOO/wsoags7UcMylN8MA1ltLLbIEwBgFbgyhDlzyoG71jS0xksWUX2OG+hcybSJOhAp/UI6b'

LOCAL = os.environ.get("LOCAL", None)

GENERATE_POSTMAN_COLLECTION = False

if LOCAL:
    SQLALCHEMY_DATABASE_URI = 'postgresql://{{ postgresql_username }}:8GShwQeSMVULP0z1NcE+19QfYcYWKi@172.17.0.2:5432/safeboda'

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    GENERATE_POSTMAN_COLLECTION = os.environ.get("GENERATE_POSTMAN_COLLECTION", None)

    SERVER_NAME = "localhost:8080"

else:
    if os.environ.get('GAE_INSTANCE'):
        SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{{ postgresql_username }}:8GShwQeSMVULP0z1NcE+19QfYcYWKi@35.196.21.230:5432/safeboda'

    SQLALCHEMY_POOL_SIZE = 6
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME = SERVER_PREFIX

PROJECT_ID = 'safeboda-213615'

DEFAULT_CREDIT = 100.0
CODE_LENGTH = 12

Expiration_time_Years = 0
Expiration_time_Months = 0
Expiration_time_Days = 30
