from dynaconf import FlaskDynaconf
from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# automatic settings
FlaskDynaconf(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

admin = Admin(
    app,
    name='Eufraten',
    template_mode='bootstrap3',
)

if __name__ == '__main__':
    app.run()
