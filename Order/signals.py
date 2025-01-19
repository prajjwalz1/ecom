from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import ShippingDetails
from dotenv import load_dotenv
load_dotenv()

from .models import Order
from django.core.mail import send_mail


from .task import send_email_task
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings



@receiver(post_save, sender=ShippingDetails)
def send_admin_notification_on_order(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        print("Signal triggered..................................................")
        shipping_details = instance
        print(shipping_details)

        # Prepare email content

# from your_app_name.tasks import send_email_task
# from django.conf import settings

# def send_order_email(instance, order):
        subject = 'New Order and Payment Received'
        admin_message = (
            f"A new order has been received!\n\n"
            f"Order ID: {order.id}\n"
            f"Total Amount: {order.price_after_discount}\n"
            f"Payment Status: {order.payment_status}\n\n"
            f"View your Order: https://api.infoteckstore.com/order/vieworder?order_id={order.id}&response_type=template\n\n"
            "Please log in to the admin panel for further details."
        )

        client_message = (
            f"Your order has been received!\n\n"
            f"Order ID: {instance.id}\n"
            f"Total Amount: {instance.order.price_after_discount}\n"
            f"Payment Status: {instance.order.payment_status}\n\n"
            f"View your Order: https://api.infoteckstore.com/order/vieworder?order_id={order.id}&response_type=template\n\n"
            "Thank you for shopping with us!"
        )

        # Send emails using Celery tasks
        send_email_task.delay(subject, admin_message, settings.ADMIN_EMAIL)

        if shipping_details and shipping_details.email:  # Check if shipping details exist
            send_email_task.delay(subject, client_message, shipping_details.email)
