import pytest

from app import create_app, db
from app.models import Usuario


@pytest.fixture
def app():
    app = create_app(testing=True)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def crear_usuario(app, rol, email=None, clave="Clave123!"):
    """Crea un usuario directamente en la base y devuelve su id."""
    email = email or f"{rol}@test.local"
    with app.app_context():
        u = Usuario(nombre=rol.capitalize(), email=email, rol=rol)
        u.set_password(clave)
        db.session.add(u)
        db.session.commit()
        return u.id


def login(client, rol, clave="Clave123!"):
    return client.post("/auth/login", data={"email": f"{rol}@test.local", "password": clave})


@pytest.fixture
def entrar(app, client):
    """Crea un usuario del rol dado e inicia sesión. Uso: entrar('mesero')."""
    def _entrar(rol):
        crear_usuario(app, rol)
        login(client, rol)
    return _entrar
