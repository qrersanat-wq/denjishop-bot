from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PRODUCTS

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Сделать заказ", callback_data="order")],
        [InlineKeyboardButton(text="📦 Статус заказов", callback_data="status")]
    ])

def products_kb():
    rows = []
    for code, title, price in PRODUCTS:
        rows.append([InlineKeyboardButton(text=f"{title} — {price} ₸", callback_data=f"product:{code}")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
