from dynaconf import FlaskDynaconf
from flask import redirect, request, abort, url_for, Flask
from flask_admin import AdminIndexView, expose, Admin
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import current_user
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security, LoginForm, url_for_security, hash_password
from flask_sqlalchemy import SQLAlchemy
from wtforms import PasswordField

app = Flask(__name__)

# automatic settings
FlaskDynaconf(app)

db = SQLAlchemy(app)

import models as model  # noqa

migrate = Migrate(app, db)

user_datastore = SQLAlchemyUserDatastore(db, model.User, model.Role)
security = Security(app, user_datastore)


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


@app.context_processor
def login_context():
    return {
        'url_for_security': url_for_security,
        'login_user_form': LoginForm(),
    }


DebugToolbarExtension(app)


class HomeView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('home.html')


class BaseView(ModelView):
    allowed_roles = []

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


class RBACView(BaseView):
    def is_accessible(self):
        # set accessibility...
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        # roles not tied to ascending permissions...
        if not current_user.has_role('export'):
            self.can_export = False

        # roles with ascending permissions...
        if current_user.has_role('admin'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True

        if not any(current_user.has_role(role) for role in self.allowed_roles):
            return False

        if current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True

        if current_user.has_role('read'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            self.can_export = False
            return True

        return False


class LoggedInView(RBACView):
    allowed_roles = ['logged_in']


class SuperView(BaseView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        return False


class UserView(SuperView):
    form_excluded_columns = ["password", "confirmed_at"]
    column_exclude_list = ["password", "confirmed_at"]
    form_extra_fields = {
        'update_password': PasswordField('Password')
    }

    def on_model_change(self, form, model: model.User, is_created):
        data = str(form.update_password.data).strip()
        if data != '':
            model.password = hash_password(data)

    def __init__(self, session, name="Usuários", *args, **kwargs):
        super(UserView, self).__init__(model.User, session, name=name, *args, **kwargs)


admin = Admin(
    app,
    name='Eufraten',
    template_mode='bootstrap3',
    index_view=HomeView(url='/'),
    url="/",
    base_template='master.html',
)

category = "Admin"
admin.add_view(SuperView(model.Role, db.session, name="Papéis", category=category))
admin.add_view(UserView(db.session, category=category))

if __name__ == '__main__':
    app.run()
