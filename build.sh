#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py makemigrations FMS_Django_App
python manage.py makemigrations

python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate FMS_Django_App
python manage.py migrate

python manage.py collectstatic --no-input