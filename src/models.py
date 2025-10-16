from datetime import datetime

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Numeric(12, 2), default=0)
    bio = db.Column(db.Text, default='')
    is_verified = db.Column(db.Boolean, default=False)
    to_verify = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    note = db.Column(db.String(200))


Transaction.from_user = db.relationship('User', foreign_keys=[Transaction.from_id])
Transaction.to_user = db.relationship('User', foreign_keys=[Transaction.to_id])
