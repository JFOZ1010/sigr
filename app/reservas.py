from datetime import date, datetime

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user

from . import db
from .auth import rol_requerido
from .models import MESAS, Reserva

bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@bp.route("/")
@rol_requerido("cliente", "mesero", "administrador")
def lista():
    consulta = Reserva.query
    if current_user.rol == "cliente":
        consulta = consulta.filter_by(cliente_id=current_user.id)
    reservas = consulta.order_by(Reserva.fecha, Reserva.hora).all()
    return render_template("reservas/lista.html", reservas=reservas)


@bp.route("/nueva", methods=["GET", "POST"])
@rol_requerido("cliente")
def nueva():
    if request.method == "POST":
        try:
            fecha = datetime.strptime(request.form.get("fecha", ""), "%Y-%m-%d").date()
            hora = datetime.strptime(request.form.get("hora", ""), "%H:%M").time()
            personas = int(request.form.get("personas", ""))
            mesa = int(request.form.get("mesa", ""))
        except ValueError:
            return _rechazar("Completa fecha, hora, personas y mesa con valores válidos.")

        if fecha < date.today():
            return _rechazar("La fecha no puede ser pasada.")
        if personas < 1:
            return _rechazar("Debe haber al menos una persona.")
        if mesa not in MESAS:
            return _rechazar("La mesa debe estar entre 1 y 10.")
        if Reserva.query.filter_by(mesa=mesa, fecha=fecha, hora=hora, estado="activa").first():
            return _rechazar("Ya hay una reserva activa para esa mesa, fecha y hora.")

        db.session.add(Reserva(cliente_id=current_user.id, fecha=fecha, hora=hora, personas=personas, mesa=mesa))
        db.session.commit()
        flash("Reserva creada.", "success")
        return redirect(url_for("reservas.lista"))
    return render_template("reservas/nueva.html", mesas=MESAS, hoy=date.today())


def _rechazar(mensaje):
    flash(mensaje, "danger")
    return render_template("reservas/nueva.html", mesas=MESAS, hoy=date.today()), 400


@bp.route("/<int:id>/cancelar", methods=["POST"])
@rol_requerido("cliente", "administrador")
def cancelar(id):
    reserva = db.get_or_404(Reserva, id)
    if current_user.rol != "administrador" and reserva.cliente_id != current_user.id:
        abort(403)
    reserva.estado = "cancelada"
    db.session.commit()
    flash("Reserva cancelada.", "info")
    return redirect(url_for("reservas.lista"))
