# [START app]

from flask import Flask
from flask_cors import CORS

import config

from controllers import prom_code
from domain import models


def create_app(config_file=config):
    main_app = Flask(__name__,
                     static_folder="dist",
                     static_url_path='',
                     template_folder="dist")

    main_app.secret_key = config.SECRET_KEY
    main_app.config.from_object(config_file)

    main_app.register_blueprint(prom_code.prom_code_blue_print,
                                url_prefix='/api/v1/code')

    with main_app.app_context():
        models.init_app(main_app)

    CORS(main_app, resources={r"/api/*": {"origins": "*"}})

    return main_app


if config.GENERATE_POSTMAN_COLLECTION:
    import json

    app = create_app()
    with app.app_context():
        urlvars = False  # Build query strings in URLs
        swagger = True  # Export Swagger specifications
        data = prom_code.api.as_postman(urlvars=urlvars, swagger=swagger)
        open("postman.json", "w").write(json.dumps(data))

app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=8080, debug=True)
# [END app]
