from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_user, logout_user

from . import db, login_manager
from .models import Usuario

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Página de inicio según el rol
INICIO_POR_ROL = {
    "cliente": "/reservas/",
    "mesero": "/pedidos/",
    "administrador": "/caja/reporte",
}


def rol_requerido(*roles):
    """Protege una ruta: sin sesión -> login; rol incorrecto -> 403."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.rol not in roles:
                abort(403)
            return vista(*args, **kwargs)
        return envoltura
    return decorador


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        clave = request.form.get("password", "")
        if not nombre or not email or len(clave) < 6:
            flash("Completa todos los campos (la clave debe tener al menos 6 caracteres).", "danger")
        elif Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "danger")
        else:
            usuario = Usuario(nombre=nombre, email=email, rol="cliente")  # siempre cliente
            usuario.set_password(clave)
            db.session.add(usuario)
            db.session.commit()
            flash("Registro exitoso. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/registro.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(request.form.get("password", "")):
            login_user(usuario)
            return redirect(INICIO_POR_ROL[usuario.rol])
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
