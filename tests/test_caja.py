from datetime import date

from app import db
from app.models import Categoria, CierreCaja, DetallePedido, Pedido, Plato
from tests.conftest import crear_usuario


def _pedido(app, estado, cantidad=2, precio=10000):
    """Crea un pedido de hoy directamente en la base."""
    with app.app_context():
        c = Categoria.query.first() or Categoria(nombre="Fuertes")
        db.session.add(c)
        db.session.flush()
        plato = Plato(nombre="Plato", precio=precio, disponible=True, categoria_id=c.id)
        pedido = Pedido(mesa=1, mesero_id=1, estado=estado)
        pedido.detalles.append(DetallePedido(plato=plato, cantidad=cantidad, precio_unitario=precio))
        db.session.add(pedido)
        db.session.commit()


def test_reporte_suma_solo_pagados(app, client, entrar):
    entrar("administrador")  # usuario id 1
    _pedido(app, "pagado", cantidad=2, precio=10000)
    _pedido(app, "pagado", cantidad=1, precio=5000)
    _pedido(app, "entregado", cantidad=9, precio=99999)  # no cuenta
    html = client.get("/caja/reporte").get_data(as_text=True)
    assert "$25.000" in html
    assert "99.999" not in html


def test_no_permite_dos_cierres_misma_fecha(app, client, entrar):
    entrar("administrador")
    _pedido(app, "pagado")
    r1 = client.post("/caja/cierre", data={"fecha": date.today().isoformat()})
    r2 = client.post("/caja/cierre", data={"fecha": date.today().isoformat()})
    assert r1.status_code == 302
    assert r2.status_code == 400
    assert "Ya existe un cierre" in r2.get_data(as_text=True)
    with app.app_context():
        assert CierreCaja.query.count() == 1
