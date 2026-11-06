from datetime import date, timedelta

from app.models import Reserva


def _datos(dias=1, hora="20:00", mesa="3"):
    fecha = (date.today() + timedelta(days=dias)).isoformat()
    return {"fecha": fecha, "hora": hora, "personas": "4", "mesa": mesa}


def test_crear_reserva(app, client, entrar):
    entrar("cliente")
    r = client.post("/reservas/nueva", data=_datos())
    assert r.status_code == 302
    with app.app_context():
        reserva = Reserva.query.one()
        assert reserva.mesa == 3 and reserva.personas == 4 and reserva.estado == "activa"


def test_rechazar_conflicto_mesa_fecha_hora(app, client, entrar):
    entrar("cliente")
    client.post("/reservas/nueva", data=_datos())
    r = client.post("/reservas/nueva", data=_datos())
    assert r.status_code == 400
    with app.app_context():
        assert Reserva.query.count() == 1


def test_rechazar_fecha_pasada(app, client, entrar):
    entrar("cliente")
    r = client.post("/reservas/nueva", data=_datos(dias=-1))
    assert r.status_code == 400
    with app.app_context():
        assert Reserva.query.count() == 0
