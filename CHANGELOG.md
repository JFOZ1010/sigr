# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [versionado semántico](https://semver.org/lang/es/).

## [1.0.0] - 2026-11-05

### Agregado
- **Base:** estructura del proyecto (`create_app` + blueprints), modelos de datos y configuración con SQLite.
- **Autenticación:** registro de clientes, inicio y cierre de sesión, contraseñas con hash y decorador `rol_requerido`.
- **Menú digital:** consulta pública del menú por categoría; CRUD de categorías y platos para el administrador.
- **Pedidos:** creación de pedidos por mesa, flujo de estados `pendiente → en_preparacion → listo → entregado → pagado`, API `/pedidos/api/activos` y actualización de la tabla cada 5 s.
- **Reservas:** reservas de clientes con validación de fecha y conflictos de mesa/fecha/hora; cancelación.
- **Caja y reportes:** reporte diario de ventas por plato y cierre de caja único por fecha.
- **Datos de demo:** script `seed.py`.
- **Pruebas:** 20 pruebas con pytest.
- **CI:** flujo de GitHub Actions (compilación y pruebas).
- **Documentación:** README, modelo de datos, manual de despliegue y logo.
