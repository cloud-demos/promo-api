from flask import Flask

from flask_migrate import Migrate
import config

main_app = Flask(__name__,
                 static_folder="dist",
                 static_url_path='',
                 template_folder="dist")
from domain import models
main_app.run(host='localhost', port=8080, debug=True)

with main_app.app_context():
    models.init_app(main_app)

migrate = Migrate(main_app, models.db)

if __name__ == '__main__':
    main_app.run(host='localhost', port=8080, debug=True)

static_url_path='',