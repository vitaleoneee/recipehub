from django.contrib import admin

from recipehub.apps.reviews.models import Review, Comment

admin.site.register(Review)
admin.site.register(Comment)
