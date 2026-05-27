from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        # import signals to register them
        try:
            import inventory.signals  # noqa: F401
        except Exception:
            pass
