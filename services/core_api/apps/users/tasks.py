from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import os

@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_email: str, first_name: str):
    try:
        subject = 'Welcome to NexTask!'
        from_email = f"NexTask <{settings.DEFAULT_FROM_EMAIL}>"
        to = [user_email]

        html_content = render_to_string('emails/welcome.html', {
            'first_name': first_name,
        })
        text_content = f"Hi {first_name}, Welcome to NexTask!"

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_email: str, first_name: str, verification_token: str):
    try:
        # verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"

        # Currently not have Frontend, for testing
        verification_url = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/auth/verify-email/?token={verification_token}"


        html_content = render_to_string('emails/email_verification.html', {
            'first_name': first_name,
            'verification_url': verification_url,
        })
        text_content = f"Hi {first_name}, verify your email: {verification_url}"

        email = EmailMultiAlternatives(
            subject='Verify your NexTask email',
            body=text_content,
            from_email=f"NexTask <{settings.DEFAULT_FROM_EMAIL}>",
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
