# cat_inventary
Gestionar ventas de repuestos caterpillar.

## Phase 0 — Inicialización

Se creó un esqueleto mínimo Django con:
- `manage.py`
- `config/` (settings, urls, wsgi)
- `core/` app con `TimeStampedModel`
- `templates/base.html`

Pasos siguientes:

1. Crear y activar un virtualenv.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar migraciones: `python manage.py migrate`.
4. Ejecutar servidor: `python manage.py runserver`.
