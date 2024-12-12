from django.core.mail import EmailMessage
from django.conf import settings
from .models import Order

def send_order_notifications(order_id, admin_email, client_email):
    try:
        # Fetch order details from database
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return "Order not found"

    # Prepare email content
    subject = 'New Order and Payment Received'
    order_url = f"https://api.infoteckstore.com/order/vieworder?order_id={order.id}&response_type=template"
    
    admin_message = (
        f"A new order has been received!\n\n"
        f"Order ID: {order.id}\n"
        f"Total Amount: {order.price_after_discount}\n"
        f"Payment Status: {order.payment_status}\n\n"
        f"View your Order: {order_url}\n\n"
        "Please log in to the admin panel for further details."
    )
    
    client_message = (
        f"Your order has been received!\n\n"
        f"Order ID: {order.id}\n"
        f"Total Amount: {order.price_after_discount}\n"
        f"Payment Status: {order.payment_status}\n\n"
        f"View your Order: {order_url}\n\n"
        "Thank you for shopping with us!"
    )

    # Send email to admin
    try:
        email_admin = EmailMessage(subject, admin_message, settings.DEFAULT_FROM_EMAIL, [admin_email])
        email_admin.send(fail_silently=False)

        # Send email to client
        if client_email:
            email_client = EmailMessage(subject, client_message, settings.DEFAULT_FROM_EMAIL, [client_email])
            email_client.send(fail_silently=False)

        return "Emails sent successfully"
    except Exception as e:
        return f"Error sending emails: {str(e)}"
