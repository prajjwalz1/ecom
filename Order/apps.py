from django.apps import AppConfig


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Order'

    def ready(self):
        #this initialize these files when the server starts that is why do this while we write signals for the model
        from . import signals