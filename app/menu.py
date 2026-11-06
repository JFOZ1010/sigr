from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)

from . import db
from .auth import rol_requerido
from .models import Categoria, DetallePedido, Plato

bp = Blueprint("menu", __name__, url_prefix="/menu")


@bp.route("/")
def index():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template("menu/index.html", categorias=categorias)


# ---------- Categorías (solo administrador) ----------

@bp.route("/categorias")
@rol_requerido("administrador")
def categorias():
    return render_template("menu/categorias.html", categorias=Categoria.query.order_by(Categoria.nombre).all())


def _guardar_categoria(categoria):
    """Valida el nombre del formulario. Devuelve True si se guardó."""
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("El nombre es obligatorio.", "danger")
        return False
    repetida = Categoria.query.filter_by(nombre=nombre).first()
    if repetida and repetida.id != categoria.id:
        flash("Ya existe una categoría con ese nombre.", "danger")
        return False
    categoria.nombre = nombre
    db.session.add(categoria)
    db.session.commit()
    return True


@bp.route("/categorias/nueva", methods=["GET", "POST"])
@rol_requerido("administrador")
def categoria_nueva():
    if request.method == "POST" and _guardar_categoria(Categoria()):
        flash("Categoría creada.", "success")
        return redirect(url_for("menu.categorias"))
    return render_template("menu/categoria_form.html", categoria=None)


@bp.route("/categorias/<int:id>/editar", methods=["GET", "POST"])
@rol_requerido("administrador")
def categoria_editar(id):
    categoria = db.get_or_404(Categoria, id)
    if request.method == "POST" and _guardar_categoria(categoria):
        flash("Categoría actualizada.", "success")
        return redirect(url_for("menu.categorias"))
    return render_template("menu/categoria_form.html", categoria=categoria)


@bp.route("/categorias/<int:id>/eliminar", methods=["POST"])
@rol_requerido("administrador")
def categoria_eliminar(id):
    categoria = db.get_or_404(Categoria, id)
    if categoria.platos:
        flash("No se puede eliminar: la categoría tiene platos.", "danger")
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada.", "success")
    return redirect(url_for("menu.categorias"))


# ---------- Platos (solo administrador) ----------

def _guardar_plato(plato):
    """Valida el formulario de plato. Devuelve True si se guardó."""
    nombre = request.form.get("nombre", "").strip()
    categoria = db.session.get(Categoria, request.form.get("categoria_id", type=int) or 0)
    precio = request.form.get("precio", type=int)
    if not nombre or categoria is None or precio is None or precio <= 0:
        flash("Nombre, categoría y un precio mayor a 0 son obligatorios.", "danger")
        return False
    plato.nombre = nombre
    plato.precio = precio
    plato.categoria_id = categoria.id
    plato.disponible = request.form.get("disponible") == "on"
    db.session.add(plato)
    db.session.commit()
    return True


@bp.route("/platos/nuevo", methods=["GET", "POST"])
@rol_requerido("administrador")
def plato_nuevo():
    if request.method == "POST" and _guardar_plato(Plato()):
        flash("Plato creado.", "success")
        return redirect(url_for("menu.index"))
    return render_template("menu/plato_form.html", plato=None, categorias=Categoria.query.all())


@bp.route("/platos/<int:id>/editar", methods=["GET", "POST"])
@rol_requerido("administrador")
def plato_editar(id):
    plato = db.get_or_404(Plato, id)
    if request.method == "POST" and _guardar_plato(plato):
        flash("Plato actualizado.", "success")
        return redirect(url_for("menu.index"))
    return render_template("menu/plato_form.html", plato=plato, categorias=Categoria.query.all())


@bp.route("/platos/<int:id>/eliminar", methods=["POST"])
@rol_requerido("administrador")
def plato_eliminar(id):
    plato = db.get_or_404(Plato, id)
    if DetallePedido.query.filter_by(plato_id=id).first():
        # Ya está en pedidos: se conserva el historial y solo se oculta
        plato.disponible = False
        db.session.commit()
        flash("El plato está en pedidos; se marcó como no disponible.", "warning")
    else:
        db.session.delete(plato)
        db.session.commit()
        flash("Plato eliminado.", "success")
    return redirect(url_for("menu.index"))
