from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(ShippingDetails)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PaymentProof)
admin.site.register(PromoCode)

