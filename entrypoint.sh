#!/bin/bash

set -e

# Wait for the database to be ready (if needed)
# while ! nc -z db 5432; do sleep 1; done

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec "$@"
