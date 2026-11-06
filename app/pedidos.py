from flask import (Blueprint, abort, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user

from . import db
from .auth import rol_requerido
from .models import MESAS, DetallePedido, Pedido, Plato

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


def _activos():
    return Pedido.query.filter(Pedido.estado != "pagado").order_by(Pedido.id).all()


@bp.route("/")
@rol_requerido("mesero", "administrador")
def lista():
    return render_template("pedidos/lista.html", pedidos=_activos())


@bp.route("/api/activos")
@rol_requerido("mesero", "administrador")
def api_activos():
    return jsonify([
        {"id": p.id, "mesa": p.mesa, "estado": p.estado, "total": p.total}
        for p in _activos()
    ])


@bp.route("/nuevo", methods=["GET", "POST"])
@rol_requerido("mesero", "administrador")
def nuevo():
    platos = Plato.query.filter_by(disponible=True).order_by(Plato.nombre).all()
    if request.method == "POST":
        error = None
        mesa = request.form.get("mesa", type=int)
        if mesa not in MESAS:
            error = "La mesa debe estar entre 1 y 10."

        # Campos "cantidad_<id_plato>"; los vacíos o en 0 se ignoran
        items = []
        for clave, valor in request.form.items():
            if not clave.startswith("cantidad_") or valor.strip() in ("", "0"):
                continue
            try:
                plato_id, cantidad = int(clave[len("cantidad_"):]), int(valor)
            except ValueError:
                error = "Cantidad inválida."
                break
            plato = db.session.get(Plato, plato_id)
            if cantidad < 1:
                error = "Las cantidades deben ser al menos 1."
            elif plato is None or not plato.disponible:
                error = "Hay un plato que no está disponible."
            else:
                items.append((plato, cantidad))
        if not error and not items:
            error = "Agrega al menos un plato al pedido."

        if error:
            flash(error, "danger")
            return render_template("pedidos/nuevo.html", platos=platos, mesas=MESAS), 400

        pedido = Pedido(mesa=mesa, mesero_id=current_user.id)
        for plato, cantidad in items:
            pedido.detalles.append(DetallePedido(plato_id=plato.id, cantidad=cantidad, precio_unitario=plato.precio))
        db.session.add(pedido)
        db.session.commit()
        flash(f"Pedido #{pedido.id} creado.", "success")
        return redirect(url_for("pedidos.lista"))
    return render_template("pedidos/nuevo.html", platos=platos, mesas=MESAS)


@bp.route("/<int:id>/estado", methods=["POST"])
@rol_requerido("mesero", "administrador")
def cambiar_estado(id):
    pedido = db.get_or_404(Pedido, id)
    siguiente = pedido.siguiente_estado
    destino = request.form.get("estado")  # estado destino (opcional)
    if siguiente is None or (destino and destino != siguiente):
        abort(400, "Transición de estado inválida.")
    pedido.estado = siguiente
    db.session.commit()
    return redirect(url_for("pedidos.lista"))
