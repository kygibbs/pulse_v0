web: gunicorn app:app --log-file=-
init: python manage.py db init
release: python manage.py db migrate
upgrade: python manage.py db upgrade
