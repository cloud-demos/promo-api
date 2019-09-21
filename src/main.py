# [START app]

from flask import Flask
from flask_cors import CORS

import config

from controllers import prom_code
from domain import models


def create_app(config_file=config):
    main_app = Flask(__name__)

    main_app.secret_key = config.SECRET_KEY
    main_app.config.from_object(config_file)

    main_app.register_blueprint(prom_code.prom_code_blue_print,
                                url_prefix='/api/v1/code')

    with main_app.app_context():
        models.init_app(main_app)

    CORS(main_app, resources={r"/api/*": {"origins": "*"}})
    # CORS(main_app, resources={r"/*": {"origins": "*"}})

    return main_app


from flask_graphql import GraphQLView
from gql import schemas

if __name__ == '__main__':
    app = create_app()

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schemas.schema,
            graphiql=True  # for having the GraphiQL interface
        ))

    app.run(host='localhost', port=8080, debug=True)
# [END app]
