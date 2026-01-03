from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from recipehub.apps.users.tasks import send_welcome_mail


@receiver(email_confirmed)
def on_email_confirmed(request, email_address, **kwargs):
    user = email_address.user
    username, email = user.username, user.email
    send_welcome_mail.delay_on_commit(username, email)
