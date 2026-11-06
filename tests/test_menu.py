from app import db
from app.models import Categoria, Plato


def _categoria(app, nombre="Entradas"):
    with app.app_context():
        c = Categoria(nombre=nombre)
        db.session.add(c)
        db.session.commit()
        return c.id


def _plato(app, categoria_id, nombre="Arepa", precio=5000):
    with app.app_context():
        p = Plato(nombre=nombre, precio=precio, disponible=True, categoria_id=categoria_id)
        db.session.add(p)
        db.session.commit()
        return p.id


def test_crear_categoria(app, client, entrar):
    entrar("administrador")
    r = client.post("/menu/categorias/nueva", data={"nombre": "Postres"})
    assert r.status_code == 302
    with app.app_context():
        assert Categoria.query.filter_by(nombre="Postres").count() == 1


def test_crear_plato(app, client, entrar):
    entrar("administrador")
    cid = _categoria(app)
    r = client.post("/menu/platos/nuevo", data={"nombre": "Empanada", "precio": "3500", "categoria_id": cid, "disponible": "on"})
    assert r.status_code == 302
    with app.app_context():
        p = Plato.query.filter_by(nombre="Empanada").one()
        assert p.precio == 3500 and p.disponible


def test_editar_plato(app, client, entrar):
    entrar("administrador")
    cid = _categoria(app)
    pid = _plato(app, cid)
    client.post(f"/menu/platos/{pid}/editar", data={"nombre": "Arepa rellena", "precio": "7000", "categoria_id": cid})
    with app.app_context():
        p = db.session.get(Plato, pid)
        assert p.nombre == "Arepa rellena" and p.precio == 7000
        assert p.disponible is False  # checkbox sin marcar


def test_eliminar_plato(app, client, entrar):
    entrar("administrador")
    pid = _plato(app, _categoria(app))
    client.post(f"/menu/platos/{pid}/eliminar")
    with app.app_context():
        assert db.session.get(Plato, pid) is None


def test_mesero_no_puede_crear_plato(app, client, entrar):
    entrar("mesero")
    cid = _categoria(app)
    r = client.post("/menu/platos/nuevo", data={"nombre": "X", "precio": "100", "categoria_id": cid})
    assert r.status_code == 403
