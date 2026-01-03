from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "recipehub.apps.users"

    def ready(self):
        import recipehub.apps.users.allauth_signals
