from django.apps import AppConfig


class SkyApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sky_api'

    def ready(self):
        from sky_api.services import planning, scheduler
        planning()
        scheduler.start()

