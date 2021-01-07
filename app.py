from flask import Flask
from flask_admin import Admin
from dynaconf import FlaskDynaconf

app = Flask(__name__)

# automatic settings
FlaskDynaconf(app)

admin = Admin(
    app,
    name='Eufraten',
    template_mode='bootstrap3',
)

if __name__ == '__main__':
    app.run()
