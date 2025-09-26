# DIBOS — Django + Wagtail Starter

## Stack
- Python 3.12+
- Django 5.x
- Wagtail 6.x
- PostgreSQL (local/dev ok with SQLite)
- Whitenoise (static), Gunicorn (WSGI), optional Daphne (ASGI)

## Setup (dev quickstart)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# SQLite by default; for Postgres, edit .env
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Deploy (high level)
- Set env vars (.env) in your server (Plesk).
- Run migrations + collectstatic.
- Serve with Gunicorn behind Nginx.
- Add HTTPS (Let's Encrypt).

## Apps included
- `pages`: HomePage + StandardPage (hero/sections) for corporate pages
- `blog`: BlogIndexPage + BlogPage
- `core`: utils (sitemaps/robots), base template

## Notes
- `config/settings/base.py` is shared; `dev.py` and `prod.py` extend it.
- Site domain/title managed in Wagtail admin (Settings → Sites).
