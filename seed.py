"""Crea las tablas y carga datos de demostración (se puede ejecutar varias veces)."""
from app import create_app, db
from app.models import Categoria, Plato, Usuario

USUARIOS = [
    ("Administrador", "admin@sigr.local", "Admin123!", "administrador"),
    ("Mesero", "mesero@sigr.local", "Mesero123!", "mesero"),
    ("Cliente", "cliente@sigr.local", "Cliente123!", "cliente"),
]

MENU = {
    "Entradas": [("Empanadas (3 uds)", 9000), ("Arepa con queso", 7500)],
    "Platos fuertes": [("Bandeja paisa", 32000), ("Sancocho de gallina", 28000),
                       ("Churrasco", 36000), ("Pechuga a la plancha", 26000)],
    "Bebidas": [("Jugo natural", 6500), ("Limonada de coco", 8500)],
}


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        for nombre, email, clave, rol in USUARIOS:
            if not Usuario.query.filter_by(email=email).first():
                u = Usuario(nombre=nombre, email=email, rol=rol)
                u.set_password(clave)
                db.session.add(u)
        for nombre_cat, platos in MENU.items():
            cat = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not cat:
                cat = Categoria(nombre=nombre_cat)
                db.session.add(cat)
                db.session.flush()
            for nombre, precio in platos:
                if not Plato.query.filter_by(nombre=nombre).first():
                    db.session.add(Plato(nombre=nombre, precio=precio, disponible=True, categoria_id=cat.id))
        db.session.commit()
        print("Datos de demostración listos.")


if __name__ == "__main__":
    main()
