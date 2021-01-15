from flask_security import RoleMixin, UserMixin
from sqlalchemy import Integer, ForeignKey, String

from app import db

# Gerenciamento de usuários

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', Integer, ForeignKey('user.id')),
    db.Column('role_id', Integer, ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, unique=True)
    description = db.Column(String)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String)
    email = db.Column(String, unique=True)
    password = db.Column(String)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email
