import os

import logging

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", 'ERROR')

eval(f'logging.basicConfig(level=logging.{LOGGING_LEVEL})')

# SERVER_PREFIX = "http://localhost:8080"
SERVER_PREFIX = "https://dev.app.safeboda.io"

JWT_SECRET = 'bmiznfu5bghP/C/aM4tQtV7M+HV16rOLulIjTypGlWnHPZze9+LB3u86hFaA2hlb+W/bvIYlpXw3'

SECRET_KEY = '5eBLvOO/wsoags7UcMylN8MA1ltLLbIEwBgFbgyhDlzyoG71jS0xksWUX2OG+hcybSJOhAp/UI6b'

LOCAL = os.environ.get("LOCAL", None)

APPLY_USER_AUTH_CONSTRAINTS = os.environ.get("APPLY_USER_AUTH_CONSTRAINTS", "yes")

USING_LOCAL_RESOURCES = LOCAL and os.environ.get("USING_LOCAL_RESOURCES", None)

GENERATE_POSTMAN_COLLECTION = False

if LOCAL:
    SQLALCHEMY_DATABASE_URI = 'postgresql://{{ postgresql_username }}:{{ postgresql_userpassword }}@172.17.0.2:5432/safeboda'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GENERATE_POSTMAN_COLLECTION = os.environ.get("GENERATE_POSTMAN_COLLECTION", None)

    SERVER_NAME = "localhost:8080"

else:
    if os.environ.get('GAE_INSTANCE'):
        SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{{ postgresql_username }}:{{ postgresql_userpassword }}@35.196.21.230:5432/safeboda'

    SQLALCHEMY_POOL_SIZE = 6
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False

PROJECT_ID = 'safeboda-213615'
