import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para continuar."
login_manager.login_message_category = "warning"


def cop(valor):
    """Formatea un número como pesos colombianos: $12.500"""
    return "${:,.0f}".format(valor or 0).replace(",", ".")


def create_app(testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-sigr-cambiar")
    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        # Ruta relativa: Flask-SQLAlchemy la ubica en instance/
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sigr.db"

    db.init_app(app)
    login_manager.init_app(app)
    app.jinja_env.filters["cop"] = cop

    from . import models  # noqa: F401  (registra las tablas)

    with app.app_context():
        db.create_all()

    # Los blueprints se registran aquí, uno por módulo.
    from . import auth
    app.register_blueprint(auth.bp)
    from . import menu
    app.register_blueprint(menu.bp)

    from . import pedidos
    app.register_blueprint(pedidos.bp)

    from . import reservas
    app.register_blueprint(reservas.bp)

    @app.route("/")
    def inicio():
        return redirect(url_for("menu.index"))

    return app
