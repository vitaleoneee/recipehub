#!/bin/bash

set -e

while ! nc -z ${DB_HOST} ${DB_PORT:-5432}; do
  echo "Waiting for database at ${DB_HOST}:${DB_PORT:-5432}..."
  sleep 1
done

if [ "$1" = "gunicorn" ]; then
    python manage.py migrate
    python manage.py collectstatic --noinput

    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"

if username and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created:", username)
else:
    print("Superuser already exists or username not set")
EOF
fi

exec "$@"