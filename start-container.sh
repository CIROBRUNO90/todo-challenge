#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

mkdir -p /var/log/supervisor
mkdir -p /var/log/django
mkdir -p /var/log/gunicorn

echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting supervisord..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
