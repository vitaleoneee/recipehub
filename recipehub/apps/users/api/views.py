from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

from recipehub.apps.users.api.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
