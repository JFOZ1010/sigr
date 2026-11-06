from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from . import db
from .auth import rol_requerido
from .models import CierreCaja, Pedido

bp = Blueprint("caja", __name__, url_prefix="/caja")


def _leer_fecha():
    """Lee ?fecha=AAAA-MM-DD (o del formulario). Por defecto, hoy."""
    texto = request.values.get("fecha")
    if not texto:
        return date.today()
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        flash("Fecha inválida; se muestra la de hoy.", "warning")
        return date.today()


def calcular_dia(fecha):
    """Ventas de los pedidos 'pagado' creados ese día."""
    inicio = datetime.combine(fecha, time.min)
    pedidos = Pedido.query.filter(
        Pedido.estado == "pagado",
        Pedido.creado_en >= inicio,
        Pedido.creado_en < inicio + timedelta(days=1),
    ).all()
    por_plato = {}
    for pedido in pedidos:
        for d in pedido.detalles:
            por_plato[d.plato.nombre] = por_plato.get(d.plato.nombre, 0) + d.cantidad
    return {
        "total": sum(p.total for p in pedidos),
        "num_pedidos": len(pedidos),
        "por_plato": sorted(por_plato.items()),
    }


@bp.route("/reporte")
@rol_requerido("administrador")
def reporte():
    fecha = _leer_fecha()
    return render_template("caja/reporte.html", fecha=fecha, datos=calcular_dia(fecha),
                           cierre=CierreCaja.query.filter_by(fecha=fecha).first())


@bp.route("/cierre", methods=["GET", "POST"])
@rol_requerido("administrador")
def cierre():
    fecha = _leer_fecha()
    if request.method == "POST":
        if CierreCaja.query.filter_by(fecha=fecha).first():
            flash(f"Ya existe un cierre para el {fecha.strftime('%d/%m/%Y')}.", "danger")
            return render_template("caja/cierre.html", fecha=fecha, datos=calcular_dia(fecha)), 400
        datos = calcular_dia(fecha)
        db.session.add(CierreCaja(fecha=fecha, total_ventas=datos["total"],
                                  num_pedidos=datos["num_pedidos"], administrador_id=current_user.id))
        db.session.commit()
        flash("Cierre de caja guardado.", "success")
        return redirect(url_for("caja.reporte", fecha=fecha.isoformat()))
    return render_template("caja/cierre.html", fecha=fecha, datos=calcular_dia(fecha))
