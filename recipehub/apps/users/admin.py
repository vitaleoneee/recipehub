from django.contrib import admin
from django.contrib.auth import get_user_model

from recipehub.apps.users.models import UserRecipeFavorite

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "date_of_birth"]


admin.site.register(UserRecipeFavorite)
