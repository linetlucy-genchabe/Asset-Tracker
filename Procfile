web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn asset_tracker.wsgi --bind 0.0.0.0:$PORT
