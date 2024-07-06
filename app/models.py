from . import db
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    organizations = db.relationship('Organization', secondary='user_organizations')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    users = db.relationship('User', secondary='user_organizations')

class UserOrganization(db.Model):
    __tablename__ = 'user_organizations'

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), primary_key=True)
