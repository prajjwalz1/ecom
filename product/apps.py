from django.apps import AppConfig



class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'



    def ready(self):
        #this initialize these files when the server starts that is why do this while we write signals for the model
        from product import signals,tasks