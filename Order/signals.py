from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.conf import settings

from dotenv import load_dotenv
load_dotenv()

from .models import Order
from django.core.mail import send_mail


@receiver(post_save, sender=Order)
def send_admin_notification_on_order(sender, instance, created, **kwargs):
    if not created and instance.payment_status == 'completed':  # Adjust according to your model's payment status field
        print("signal triggered..................................................")
        subject = 'New Order and Payment Received'
        message = (
            f"A new order has been received!\n\n"
            f"Order ID: {instance.id}\n"
            # f"Customer: {instance.customer.name}\n"
            f"Total Amount: {instance.price_after_discount}\n"
            f"Payment Status: {instance.payment_status}\n\n"
            f"View your Order: https://api.infoteckstore.com/order/vieworder?order_id={instance.id}\n\n"
            "Please log in to the admin panel for further details."
        )
        print(settings.DEFAULT_FROM_EMAIL)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )