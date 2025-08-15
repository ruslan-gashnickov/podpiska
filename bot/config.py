# bot/config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DJANGO_API_URL = os.getenv("DJANGO_API_URL")

# Добавим проверку
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")
if not DJANGO_API_URL:
    raise ValueError("DJANGO_API_URL не найден в .env файле")