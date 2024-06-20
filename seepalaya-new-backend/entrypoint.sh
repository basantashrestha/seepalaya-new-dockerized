#!/bin/sh

export POSTGRES_HOST="db"

if [ $DATABASE = "postgres" ]
then
    echo "Waiting for postgres to load..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done

    echo "postgres ready to run"
    python manage.py makemigrations
    python manage.py migrate --no-input
fi

python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL 
python es_index.py

exec "$@"
