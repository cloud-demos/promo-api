import os

import logging

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", 'ERROR')

eval(f'logging.basicConfig(level=logging.{LOGGING_LEVEL})')

# SERVER_PREFIX = "http://localhost:8080"
SERVER_PREFIX = "https://dev.app.safeboda.io"

JWT_SECRET = 'bmiznfu5bghP/C/aM4tQtV7M+HV16rOLulIjTypGlWnHPZze9+LB3u86hFaA2hlb+W/bvIYlpXw3'

SECRET_KEY = '5eBLvOO/wsoags7UcMylN8MA1ltLLbIEwBgFbgyhDlzyoG71jS0xksWUX2OG+hcybSJOhAp/UI6b'

LOCAL = os.environ.get("LOCAL", "No")

GENERATE_POSTMAN_COLLECTION = False

if LOCAL != "No":
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASS')}@{os.environ.get('DATABASE_HOST')}:5432/promo_code_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    GENERATE_POSTMAN_COLLECTION = os.environ.get("GENERATE_POSTMAN_COLLECTION", None)

    SERVER_NAME = "localhost:8080"

else:
    if os.environ.get('GAE_INSTANCE'):
        SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.environ.get('PROD_DATABASE_USER')}:{os.environ.get('PROD_DATABASE_PASS')}@{os.environ.get('PROD_DATABASE_HOST')}:5432/promo_code_db"

    SQLALCHEMY_POOL_SIZE = 6
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME = SERVER_PREFIX

PROJECT_ID = 'safeboda-213615'

DEFAULT_CREDIT = 100.0
CODE_LENGTH = 12
MILES_COST = 1.0

Expiration_time_Years = 0
Expiration_time_Months = 0
Expiration_time_Days = 30
