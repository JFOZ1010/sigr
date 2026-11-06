from app import db
from app.models import Categoria, Pedido, Plato


def _plato(app, nombre="Bandeja", precio=20000, disponible=True):
    with app.app_context():
        c = Categoria.query.first() or Categoria(nombre="Fuertes")
        db.session.add(c)
        db.session.flush()
        p = Plato(nombre=nombre, precio=precio, disponible=disponible, categoria_id=c.id)
        db.session.add(p)
        db.session.commit()
        return p.id


def _pedido(client, plato_id, cantidad=1, mesa=1):
    return client.post("/pedidos/nuevo", data={"mesa": mesa, f"cantidad_{plato_id}": cantidad})


def test_crear_pedido_y_total(app, client, entrar):
    entrar("mesero")
    p1 = _plato(app, "Bandeja", 20000)
    p2 = _plato(app, "Jugo", 6000)
    r = client.post("/pedidos/nuevo", data={"mesa": "4", f"cantidad_{p1}": "2", f"cantidad_{p2}": "1"})
    assert r.status_code == 302
    with app.app_context():
        pedido = Pedido.query.one()
        assert pedido.mesa == 4 and pedido.estado == "pendiente"
        assert pedido.total == 2 * 20000 + 6000


def test_rechazar_pedido_sin_items(app, client, entrar):
    entrar("mesero")
    _plato(app)
    r = client.post("/pedidos/nuevo", data={"mesa": "2"})
    assert r.status_code == 400
    with app.app_context():
        assert Pedido.query.count() == 0


def test_transicion_valida(app, client, entrar):
    entrar("mesero")
    _pedido(client, _plato(app))
    r = client.post("/pedidos/1/estado", data={"estado": "en_preparacion"})
    assert r.status_code == 302
    with app.app_context():
        assert db.session.get(Pedido, 1).estado == "en_preparacion"


def test_transicion_invalida(app, client, entrar):
    entrar("mesero")
    _pedido(client, _plato(app))
    r = client.post("/pedidos/1/estado", data={"estado": "pagado"})  # salta estados
    assert r.status_code == 400
    with app.app_context():
        assert db.session.get(Pedido, 1).estado == "pendiente"


def test_api_activos_solo_no_pagados(app, client, entrar):
    entrar("mesero")
    pid = _plato(app)
    _pedido(client, pid, mesa=1)
    _pedido(client, pid, mesa=2)
    with app.app_context():
        db.session.get(Pedido, 2).estado = "pagado"
        db.session.commit()
    datos = client.get("/pedidos/api/activos").get_json()
    assert [d["id"] for d in datos] == [1]
    assert set(datos[0]) == {"id", "mesa", "estado", "total"}
    assert datos[0]["total"] == 20000
