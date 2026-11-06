# Manual de despliegue (desarrollo local)

Requisitos: **Python 3.10 o superior** y `git`.

## macOS / Linux

```bash
git clone https://github.com/JFOZ1010/sigr.git
cd sigr
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py
flask --app run run
```

## Windows (PowerShell)

```powershell
git clone https://github.com/JFOZ1010/sigr.git
cd sigr
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
flask --app run run
```

Si PowerShell bloquea el script de activación: `Set-ExecutionPolicy -Scope Process RemoteSigned`.

La aplicación queda en <http://127.0.0.1:5000>.

## Variables de entorno

| Variable | Uso | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | firma de sesiones | `dev-sigr-cambiar` (solo desarrollo) |

## Regenerar la base de datos

Borra la base y vuelve a sembrar:

```bash
rm instance/sigr.db        # Windows: del instance\sigr.db
python seed.py
```

## Pruebas

```bash
pytest -v
```

Usan SQLite en memoria; no tocan `instance/sigr.db`.

## Notas

- Esto es un entorno de desarrollo (servidor de Flask). Para producción habría que usar un servidor WSGI, una `SECRET_KEY` propia y cambiar las contraseñas demo; queda fuera de esta línea base.
