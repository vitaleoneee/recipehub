from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_welcome_mail(username: str, email: str) -> None:
    if not email:
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

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
