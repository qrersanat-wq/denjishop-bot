import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7816223759:AAFP3H-yPBYRLGmW_yIIR-yhmkiLu-oIcQk")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip().isdigit()]

# Валюта и база цен (KZT). Можно вынести в БД/админку позже.
PRODUCTS = [
    # code, title, base_price_kzt
    ("d86",  "Алмазы 86",  1200),
    ("d172", "Алмазы 172",  2300),
    ("d257", "Алмазы 257",  3300),
    ("d344", "Алмазы 344",  4200),
]
UNIQUE_RANGE = (1, 97)   # суффикс уникальной суммы (тг)
DB_PATH = os.getenv("DB_PATH", "dngshop.db")
