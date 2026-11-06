from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager

ROLES = ("cliente", "mesero", "administrador")
ESTADOS = ("pendiente", "en_preparacion", "listo", "entregado", "pagado")
MESAS = range(1, 11)  # mesas válidas: 1 a 10


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")

    def set_password(self, clave):
        self.password_hash = generate_password_hash(clave)

    def check_password(self, clave):
        return check_password_hash(self.password_hash, clave)


@login_manager.user_loader
def cargar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    platos = db.relationship("Plato", backref="categoria")


class Plato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)  # pesos COP
    disponible = db.Column(db.Boolean, nullable=False, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.Integer, nullable=False)
    mesero_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.now)
    mesero = db.relationship("Usuario")
    detalles = db.relationship("DetallePedido", backref="pedido", cascade="all, delete-orphan")

    @property
    def total(self):
        return sum(d.cantidad * d.precio_unitario for d in self.detalles)

    @property
    def siguiente_estado(self):
        i = ESTADOS.index(self.estado)
        return ESTADOS[i + 1] if i + 1 < len(ESTADOS) else None


class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    plato_id = db.Column(db.Integer, db.ForeignKey("plato.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)  # copia del precio al crear
    plato = db.relationship("Plato")


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    personas = db.Column(db.Integer, nullable=False)
    mesa = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activa")  # activa | cancelada
    cliente = db.relationship("Usuario")


class CierreCaja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False)
    total_ventas = db.Column(db.Integer, nullable=False)
    num_pedidos = db.Column(db.Integer, nullable=False)
    administrador_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
