from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import OrderFSM
from config import PRODUCTS
from utils import build_unique_amount
from db import insert_order

router = Router()

PRODUCT_INDEX = {code: (title, price) for code, title, price in PRODUCTS}

@router.callback_query(OrderFSM.waiting_product, F.data.startswith("product:"))
async def picked_product(cb: CallbackQuery, state: FSMContext):
    code = cb.data.split(":", 1)[1]
    if code not in PRODUCT_INDEX:
        await cb.answer("Неизвестный пакет.", show_alert=True)
        return
    title, price = PRODUCT_INDEX[code]
    await state.update_data(product_code=code, product_title=title, base_price=price)
    await state.set_state(OrderFSM.waiting_game_id)
    await cb.message.edit_text(
        f"Вы выбрали: <b>{title}</b>\n\nОтправьте, пожалуйста, <b>Game ID</b>."
    )
    await cb.answer()

@router.message(OrderFSM.waiting_game_id)
async def got_game_id(msg: Message, state: FSMContext):
    text = msg.text.strip()
    import re
    match = re.match(r"(\d+)\s*\(([^)]+)\)", text)
    if not match:
        await msg.answer("Неверный формат. Введите как: 12345678 (1234)")
        return

    gid, server = match.groups()
    await state.update_data(game_id=gid, game_server=server)

    # Берём данные по продукту
    data = await state.get_data()
    code = data["product_code"]
    title = data["product_title"]
    base_price = data["base_price"]

    # Генерируем уникальную сумму
    uniq_amount = build_unique_amount(base_price)

    order_id = insert_order(
        tg_user_id=msg.from_user.id,
        product_code=code,
        product_title=title,
        base_price=base_price,
        uniq_amount=uniq_amount,
        game_id=gid,
        game_server=server
    )

    await state.clear()
    text = (
        f"🎉 Ваш заказ <b>#{order_id}</b> успешно создан!\n\n"
        f"💎 Товар: <b>{title}</b>\n"
        f"💰 К оплате: <b>{uniq_amount} ₸</b>\n"
        f"🏷 Game ID: <b>{gid}</b>\n"
        f"🌐 Сервер: <b>{server}</b>\n\n"
        f"📌 Реквизиты для оплаты: <i>Kaspi (уточним детали)</i>\n"
        f"❗ Комментарий не нужен, убедитесь, что сумма совпадает точно.\n\n"
        f"✅ После оплаты бот автоматически проверит платёж и продолжит оформление."
    )
    await msg.answer(text)
