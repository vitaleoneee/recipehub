import logging
from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_mail(self, username: str, email: str) -> None:
    if not email:
        logger.warning(
            f"Attempted to send welcome email without email address for user: {username}"
        )
        return

    subject = "Welcome to Recipe Hub!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email

    text_content = f"""
        Hi, {username}!

        Thank you for joining RecipeHub — the place where delicious recipes find their lovers. 😋

        Get started now and find your next culinary masterpiece!
        Go to recipes: {settings.SITE_URL}

        With love,
        The RecipeHub Team ❤️
    """

    html_content = f"""
        <p>Hi, {username}!</p>

        <p>Thank you for joining <strong>RecipeHub</strong> — the place where delicious recipes find their lovers. 😋</p>

        <p>Get started now and find your next culinary masterpiece!<br>
        <a href="{settings.SITE_URL}">Go to recipes</a></p>

        <p>With love,<br>
        The RecipeHub Team ❤️</p>
    """

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Welcome email successfully sent to {email} for user {username}")

    except SMTPException as e:
        logger.error(
            f"SMTP error sending welcome email to {email} for user {username}: {str(e)}",
            exc_info=True,
        )
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))

    except Exception as e:
        logger.error(
            f"Unexpected error sending welcome email to {email} for user {username}: {str(e)}",
            exc_info=True,
        )
