import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN. Проверьте файл .env / переменные окружения на BotHost.")
if not ADMIN_ID:
    raise RuntimeError("Не задан ADMIN_ID. Проверьте файл .env / переменные окружения на BotHost.")

# ---------- Цены и условия ----------

# Аренда микронаушника на день (без суфлёра)
PRICE_DAY = 700

# Услуга "микронаушник + суфлёр"
PRICE_HELPER_BASE = 700         # аренда устройства
PRICE_HELPER_BLOCK = 1000       # доплата за суфлёра за каждые 1.5 часа
HELPER_BLOCK_HOURS = 1.5

# Залог
DEPOSIT_MONEY = 3000            # залог деньгами, руб.
DEPOSIT_ALT_TEXT = "студенческий билет"  # альтернатива залогу

# Варианты длительности услуги "с суфлёром" (в блоках по 1.5 часа)
HELPER_DURATION_OPTIONS = [1, 2, 3, 4]  # -> 1.5ч, 3ч, 4.5ч, 6ч
