# [START app]
import logging

from flask import Flask
from flask_cors import CORS

import config

from controllers import prom_code
from domain import models

main_app = Flask(__name__,
                 static_folder="dist",
                 static_url_path='',
                 template_folder="dist")

main_app.secret_key = config.SECRET_KEY
main_app.config.from_object(config)

main_app.register_blueprint(prom_code.prom_code_blue_print, url_prefix='/api/v1/code')

with main_app.app_context():
    models.init_app(main_app)

cors = CORS(main_app, resources={r"/api/*": {"origins": "*"}})


@main_app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if config.GENERATE_POSTMAN_COLLECTION:
    import json

    with main_app.app_context():
        urlvars = False  # Build query strings in URLs
        swagger = True  # Export Swagger specifications
        data = prom_code.api.as_postman(urlvars=urlvars, swagger=swagger)
        open("postman.json", "w").write(json.dumps(data))

if __name__ == '__main__':
    main_app.run(host='localhost', port=8080, debug=True)
# [END app]
