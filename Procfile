release: alembic upgrade head
web: gunicorn webhook_bot:app --workers=4 & python morethanmarvin.py & python webhook_keybase_service