from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import ShippingDetails
from dotenv import load_dotenv
load_dotenv()

from .models import Order
from django.core.mail import send_mail


import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

def send_email_in_thread(subject, message, to_email):
    """
    Function to send email in a separate thread to avoid blocking the main thread.
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error sending email: {e}")

@receiver(post_save, sender=ShippingDetails)
def send_admin_notification_on_order(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        print("Signal triggered..................................................")
        shipping_details = instance
        print(shipping_details)

        # Prepare email content
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

        # Create and start the thread to send email to admin
        threading.Thread(target=send_email_in_thread, args=(subject, admin_message, settings.ADMIN_EMAIL)).start()

        # Create and start the thread to send email to the shipping details email
        if shipping_details and shipping_details.email:  # Check if shipping details exist
            threading.Thread(target=send_email_in_thread, args=(subject, client_message, shipping_details.email)).start()
