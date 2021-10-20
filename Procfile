release: alembic upgrade head
web: gunicorn webhook_bot:app --workers=4
bot: python morethanmarvin.py
webhook_keybase_service: python webhook_keybase_service