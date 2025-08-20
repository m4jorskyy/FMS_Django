#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Stwórz fresh migracje bez admin/contenttypes
python manage.py makemigrations FMS_Django_App
python manage.py migrate auth
python manage.py migrate FMS_Django_App
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --no-input