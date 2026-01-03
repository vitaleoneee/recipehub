from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from recipehub.apps.users.tasks import send_welcome_mail


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    username, email = user.username, user.email
    send_welcome_mail.delay_on_commit(username, email)
