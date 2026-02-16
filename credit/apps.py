# credit/apps.py
from django.apps import AppConfig
import os

class CreditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "credit"

    def ready(self):
        # Only run once, not on autoreload
        if os.environ.get("RUN_MAIN") == "true":
            # Import the loader function but don't execute immediately
            from .services.ingestion import load_initial_data_safe
            # Run it in a background thread so it doesn't block server startup
            import threading
            threading.Thread(target=load_initial_data_safe, daemon=True).start()