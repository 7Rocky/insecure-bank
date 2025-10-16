import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(32).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from models import User
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin_password = os.urandom(32).hex()

            with open('admin_password.txt', 'w') as f:
                f.write(admin_password)

            admin = User(username='admin', is_admin=True, is_verified=True, balance=1_000_000, bio='Soy el administrador de este banco online. Si tienes cualquier problema, házmelo saber')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

        if not User.query.filter_by(username='victim').first():
            victim_password = os.urandom(32).hex()

            with open('victim_password.txt', 'w') as f:
                f.write(victim_password)

            victim = User(username='victim', balance=1337, bio='¡Hola, acabo de crearme una cuenta!')
            victim.set_password(victim_password)
            db.session.add(victim)
            db.session.commit()

    return app


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))