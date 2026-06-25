import os

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from apps.core.users.models import User

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
        user = User.objects.get(email=user_email)
        if user.is_verified:
            return

        verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}&email={user_email}"


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

@shared_task(bind=True, max_retries=3)
def send_reminder_email(self, user_email: str, first_name: str,
                        task_title: str, project_name: str, due_date: str):
    try:
        html_content = render_to_string('emails/task_reminder.html', {
            'first_name': first_name,
            'task_title': task_title,
            'project_name': project_name,
            'due_date': due_date,
        })
        text_content = (
            f"Hi {first_name}, your task '{task_title}' "
            f"in project '{project_name}' is due tomorrow ({due_date})."
        )

        email = EmailMultiAlternatives(
            subject=f"Reminder: '{task_title}' is due tomorrow!",
            body=text_content,
            from_email=f"NexTask <{settings.DEFAULT_FROM_EMAIL}>",
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_email: str, first_name: str, token: str):
    try:
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"

        html_content = render_to_string('emails/password_reset.html', {
            'first_name': first_name,
            'reset_url': reset_url,
        })
        text_content = f"Hi {first_name}, reset your password: {reset_url}"

        email = EmailMultiAlternatives(
            subject='Reset your NexTask password',
            body=text_content,
            from_email=f"NexTask <{settings.DEFAULT_FROM_EMAIL}>",
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
