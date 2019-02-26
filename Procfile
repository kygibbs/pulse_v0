web: gunicorn app:app --log-file=-
init: python manage.py db init
release: python manage.py migrate
upgrade: python manage.py db upgrade
