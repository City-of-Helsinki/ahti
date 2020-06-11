#!/bin/bash

set -e

if [ -z "$SKIP_DATABASE_CHECK" -o "$SKIP_DATABASE_CHECK" = "0" ]; then
  until nc -z -v -w30 "$DATABASE_HOST" 5432
  do
    echo "Waiting for postgres database connection..."
    sleep 1
  done
  echo "Database is up!"
fi

# Restore a DB dump
if [[ "$RESTORE_DB_DUMP_DEV" = "1" ]]; then
    echo "Restoring a database dump over the current db..."
    wormhole receive --hide-progress --accept-file -o /tmp/pg.sql "$RESTORE_DB_DUMP_MWH_CODE"
    psql "$DATABASE_URL" -f /tmp/pg.sql
fi

# Apply database migrations
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py makemigrations
    ./manage.py migrate --noinput
fi

# Create superuser
if [[ "$CREATE_SUPERUSER" = "1" ]]; then
    ./manage.py add_admin_user -u admin -p admin -e admin@example.com
    echo "Admin user created with credentials admin:admin (email: admin@example.com)"
fi

# Import / update feature data in the DB
if [[ "$IMPORT_FEATURES" = "1" ]]; then
    ./manage.py import_features
    echo "Imported features from configured sources"
fi

# Start server
if [[ ! -z "$@" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    ./manage.py runserver 0.0.0.0:8082
else
    uwsgi --ini .prod/uwsgi.ini
fi
