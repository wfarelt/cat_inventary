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

## Desarrollo

Comandos útiles para desarrollo local:

- Crear y activar entorno virtual (Windows PowerShell):

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

- Activar (bash / WSL / macOS):

	```bash
	python -m venv .venv
	source .venv/bin/activate
	```

- Instalar dependencias:

	```bash
	pip install -r requirements.txt
	```

- Migraciones y datos iniciales:

	```bash
	python manage.py migrate
	python manage.py loaddata initial_data.json  # si existe
	python manage.py setup_roles               # crear grupos y permisos
	```

- Ejecutar servidor:

	```bash
	python manage.py runserver
	```

## Tests

Ejecutar la suite de tests:

```bash
pytest
# o
python manage.py test
```

## Desarrollo de features

- Trabajar en una rama por feature: `git checkout -b feat/mi-feature`.
- Ejecutar pruebas y linters antes de push.
- Abrir PR describiendo cambios y pasos para probar.

Si necesitas que añada instrucciones específicas para despliegue, configuración de `MEDIA_ROOT` o integración con S3, dime y las añado.

## Phase 3 — Inventario

Se implementó un núcleo de inventario (app `inventory`) que soporta movimientos, kardex, historial de costos y precios, ajustes y devoluciones.

- Endpoints principales:
	- `/inventory/` — lista de movimientos
	- `/inventory/create/` — registrar ajuste / devolución (no permite crear compras/ventas manuales)
	- `/inventory/kardex/` — vista kardex y `?export=xlsx` para exportar

- Lógica central en: `inventory/services.py` (increase/decrease/reserve/release/adjust/register_return, update_last_cost).
- Modelos: `StockMovement`, `ProductCostHistory`, `ProductPriceHistory` en `inventory/models.py`.
- Admin: `inventory/admin.py` registra movimientos e historiales para inspección.

- Configuración relevante:
	- `INVENTORY_AUTO_HISTORY` (bool, por defecto `True`) controla signals que crean automáticamente registros de costo/precio cuando `Product` cambia.

- Reglas importantes:
	- `available_stock = stock - stock_reserved` (propiedad en `products.Product`).
	- No se permite stock disponible negativo; las funciones lanzan `InventoryError` y el UI debe mostrar "Stock insuficiente".
	- Las actualizaciones de costo usan la regla LAST COST (se guarda `ProductCostHistory` y se actualiza `product.cost`).

- Tests: hay pruebas unitarias en `inventory/tests/` que cubren servicios y signals.

Comandos útiles:
```bash
python manage.py migrate
python manage.py test inventory
python manage.py runserver
```

Si quieres que añada ejemplos de uso, endpoints API REST, o una guía para la migración a producción (S3, backups, CI), lo hago a continuación.

## Phase 4 — Purchases (Compras)

El módulo de compras (`app: purchases`) implementa el flujo de órdenes de compra, control de stock y auditoría básica.

- Flujo: `DRAFT` → `CONFIRMED` → `CANCELLED`.
- Rutas principales (ver `purchases/urls.py`):
	- `/purchases/` — lista
	- `/purchases/create/` — crear (DRAFT)
	- `/purchases/<pk>/` — detalle
	- `/purchases/<pk>/confirm/` — confirmar
	- `/purchases/<pk>/cancel/` — anular

- Servicios relevantes (`purchases/services.py`):
	- `confirm_purchase(purchase, user=None, ip=None)` — valida, recalcula totales, aumenta stock (usa `inventory.services.increase_stock`), aplica regla LAST COST y crea movimientos y `ProductCostHistory`. Registra un `PurchaseAudit` con evento `CONFIRMED`.
	- `cancel_purchase(purchase, user=None, ip=None)` — revierte stock con movimientos `MANUAL_CORRECTION` y registra `PurchaseAudit` con evento `CANCELLED`.

- Auditoría:
	- Modelo `PurchaseAudit` en `purchases/models.py` registra `purchase`, `event`, `user`, `ip`, `detail`, `created_at`.
	- Señales (`purchases/signals.py`) crean eventos `CREATED` y `EDITED` al guardar una `Purchase`.
	- Para incluir la IP cuando la acción proviene de una vista, pase `ip=request.META.get('REMOTE_ADDR')` al llamar a los servicios. Si su app está detrás de proxy, extraiga `HTTP_X_FORWARDED_FOR` según corresponda.

- Ejemplo de uso en vista (simplificado):

	```python
	from django.shortcuts import get_object_or_404, redirect
	from purchases.models import Purchase
	from purchases import services as purchase_services

	def purchase_confirm(request, pk):
			p = get_object_or_404(Purchase, pk=pk)
			purchase_services.confirm_purchase(p, user=request.user, ip=request.META.get('REMOTE_ADDR'))
			return redirect('purchases:purchase_detail', pk=pk)
	```

- Admin/UI:
	- `Purchase`, `PurchaseItem` y `PurchaseAudit` están registrados en el admin para inspección y acciones desde la interfaz.

- Tests:
	- Hay pruebas en `purchases/tests/` que cubren confirmación, anulación y auditoría.
	- Ejecutar:

		```bash
		python manage.py test purchases
		```

Notas:
- Asegúrate de incluir `purchases` en `INSTALLED_APPS` y las rutas en `config/urls.py` con `path('purchases/', include('purchases.urls'))`.
- Si quieres soporte avanzado de auditoría (metadatos adicionales, export, o webhooks), puedo añadir un modelo independiente o integrar un sistema de logging externo.

