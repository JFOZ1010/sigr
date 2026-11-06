from app.models import Usuario
from tests.conftest import crear_usuario


def test_registro_crea_cliente(app, client):
    r = client.post("/auth/registro", data={"nombre": "Ana", "email": "ana@test.local", "password": "secreto1", "rol": "administrador"})
    assert r.status_code == 302
    with app.app_context():
        u = Usuario.query.filter_by(email="ana@test.local").one()
        assert u.rol == "cliente"  # aunque se intente enviar otro rol


def test_login_correcto(app, client):
    crear_usuario(app, "mesero")
    r = client.post("/auth/login", data={"email": "mesero@test.local", "password": "Clave123!"})
    assert r.status_code == 302
    assert r.headers["Location"] == "/pedidos/"


def test_login_clave_incorrecta(app, client):
    crear_usuario(app, "cliente")
    r = client.post("/auth/login", data={"email": "cliente@test.local", "password": "mala"})
    assert r.status_code == 200
    assert "incorrectos" in r.get_data(as_text=True)


def test_ruta_protegida_sin_sesion_redirige(app, client):
    from app.auth import rol_requerido

    # ruta de prueba protegida con el decorador
    app.add_url_rule("/protegida", "protegida", rol_requerido("administrador")(lambda: "ok"))
    r = client.get("/protegida")
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]
