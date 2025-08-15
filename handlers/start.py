from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu_kb, products_kb
from states import OrderFSM

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я помогу оформить заказ. Выберите действие:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "status")
async def status_menu(cb: CallbackQuery):
    from db import list_pending_orders
    rows = list_pending_orders(cb.from_user.id)
    if not rows:
        await cb.message.edit_text("У вас нет ожидающих оплат заказов.", reply_markup=main_menu_kb())
        await cb.answer()
        return
    lines = ["<b>Ожидают оплаты:</b>"]
    for r in rows:
        lines.append(f"• #{r['id']}: {r['product_title']} — к оплате <b>{r['uniq_amount']} ₸</b>")
    await cb.message.edit_text("\n".join(lines), reply_markup=main_menu_kb())
    await cb.answer()

@router.callback_query(F.data == "order")
async def start_order(cb: CallbackQuery, state):
    await state.set_state(OrderFSM.waiting_product)
    await cb.message.edit_text("Выберите пакет:", reply_markup=products_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("back:") & F.data.endswith("menu"))
async def back_to_menu(cb: CallbackQuery, state):
    await state.clear()
    await cb.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await cb.answer()
