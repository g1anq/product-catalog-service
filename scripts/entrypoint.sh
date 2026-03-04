#!/bin/sh
echo "Waiting for postgres..."

echo "Running database migrations..."
alembic upgrade head

exec "$@"