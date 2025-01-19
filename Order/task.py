from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(subject, message, to_email):
    try:
        send_mail(subject, message, None, [to_email], fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {e}")