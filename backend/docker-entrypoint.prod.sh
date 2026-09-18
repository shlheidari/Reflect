#!/bin/sh
# Collects static assets on every start (cheap, idempotent, needs real env
# vars which only exist at container runtime — see backend/Dockerfile.prod).
# Deliberately does NOT run migrations: schema changes are a manual,
# explicit step (see docs/DEPLOYMENT.md) rather than something that fires
# silently on every container restart.
set -e

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile - \
    --error-logfile -
