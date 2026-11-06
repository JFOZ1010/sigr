from app.models import CierreCaja, Pedido, Plato
from tests.conftest import crear_usuario, login


def test_flujo_completo(app, client):
    crear_usuario(app, "administrador")
    crear_usuario(app, "mesero")

    # El administrador crea categoría y plato
    login(client, "administrador")
    client.post("/menu/categorias/nueva", data={"nombre": "Fuertes"})
    client.post("/menu/platos/nuevo", data={"nombre": "Bandeja paisa", "precio": "28000", "categoria_id": "1", "disponible": "on"})
    client.get("/auth/logout")

    # El mesero crea un pedido y lo avanza hasta pagado
    login(client, "mesero")
    with app.app_context():
        plato_id = Plato.query.one().id
    client.post("/pedidos/nuevo", data={"mesa": "5", f"cantidad_{plato_id}": "2"})
    for estado in ("en_preparacion", "listo", "entregado", "pagado"):
        r = client.post("/pedidos/1/estado", data={"estado": estado})
        assert r.status_code == 302
    client.get("/auth/logout")

    # El administrador hace el cierre y el total coincide
    login(client, "administrador")
    client.post("/caja/cierre")
    with app.app_context():
        assert Pedido.query.one().estado == "pagado"
        cierre = CierreCaja.query.one()
        assert cierre.total_ventas == 2 * 28000
        assert cierre.num_pedidos == 1
