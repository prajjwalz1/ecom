from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import ShippingDetails
from dotenv import load_dotenv
load_dotenv()

from .models import Order
from django.core.mail import send_mail


@receiver(post_save, sender=ShippingDetails)
def send_admin_notification_on_order(sender, instance, created, **kwargs):
    if created:  # Adjust according to your model's payment status field
        order=instance.order
        print("Signal triggered..................................................")
        shipping_details=instance
        print(shipping_details)
        
        # Prepare email content
        subject = 'New Order and Payment Received'
        admin_message = (
            f"A new order has been received!\n\n"
            f"Order ID: {order.id}\n"
            # f"Customer: {instance.customer.name}\n"
            f"Total Amount: {order.price_after_discount}\n"
            f"Payment Status: {order.payment_status}\n\n"
            f"View your Order: https://api.infoteckstore.com/order/vieworder?order_id={order.id}&response_type=template\n\n"
            "Please log in to the admin panel for further details."
        )
        
        client_message = (
            f"Your order has been received!\n\n"
            f"Order ID: {instance.id}\n"
            # f"Customer: {instance.customer.name}\n"
            f"Total Amount: {instance.order.price_after_discount}\n"
            f"Payment Status: {instance.order.payment_status}\n\n"
            f"View your Order: https://api.infoteckstore.com/order/vieworder?order_id={order.id}&response_type=template\n\n"
            "Please log in to the admin panel for further details."
        )
        # Send email to admin
        print(shipping_details.email)
        send_mail(
            subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        # Send email to shipping details email
        if shipping_details and shipping_details.email:  # Check if shipping details exist
            send_mail(
                subject,
                client_message,
                settings.DEFAULT_FROM_EMAIL,
                [shipping_details.email],
                fail_silently=False,
            )