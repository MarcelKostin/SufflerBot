from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import config
import storage
from keyboards import duration_keyboard, deposit_keyboard, contact_keyboard, confirm_keyboard
from states import (
    CHOOSING_SERVICE, ENTERING_DATE, CHOOSING_DURATION, CHOOSING_DEPOSIT,
    ENTERING_CONTACT, CONFIRMING, SERVICE_DAY, SERVICE_HELPER,
)

SERVICE_NAMES = {
    SERVICE_DAY: "Наушник на день",
    SERVICE_HELPER: "Наушник с суфлёром",
}


# ---------- Шаг 1: услуга ----------

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service = query.data
    context.user_data["service"] = service
    context.user_data["service_name"] = SERVICE_NAMES[service]

    await query.edit_message_text(
        f"Вы выбрали: <b>{SERVICE_NAMES[service]}</b>\n\n"
        "📅 На какую дату нужна аренда? Напишите в формате ДД.ММ.ГГГГ\n"
        "(например: 05.10.2026)",
        parse_mode="HTML",
    )
    return ENTERING_DATE


# ---------- Шаг 2: дата ----------

async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_text = update.message.text.strip()
    if len(date_text) < 6:
        await update.message.reply_text(
            "Пожалуйста, укажите дату в формате ДД.ММ.ГГГГ (например: 05.10.2026)."
        )
        return ENTERING_DATE

    context.user_data["date"] = date_text

    if context.user_data["service"] == SERVICE_HELPER:
        await update.message.reply_text(
            "⏱ На сколько часов нужен суфлёр?",
            reply_markup=duration_keyboard(),
        )
        return CHOOSING_DURATION
    else:
        context.user_data["duration_text"] = "1 день"
        context.user_data["price"] = config.PRICE_DAY
        await update.message.reply_text(
            "Как оформим залог?",
            reply_markup=deposit_keyboard(),
        )
        return CHOOSING_DEPOSIT


# ---------- Шаг 3: длительность (только для услуги с суфлёром) ----------

async def choose_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "dur_custom":
        await query.edit_message_text(
            "Напишите нужную длительность текстом (например: «2 часа» или «5 часов»)."
        )
        return CHOOSING_DURATION

    blocks = int(data.split("_")[1])
    hours = blocks * config.HELPER_BLOCK_HOURS
    price = config.PRICE_HELPER_BASE + blocks * config.PRICE_HELPER_BLOCK

    context.user_data["duration_text"] = f"{hours:g} ч"
    context.user_data["price"] = price

    await query.edit_message_text(
        f"Длительность: {hours:g} ч, стоимость: {price}₽\n\n"
        "Как оформим залог?",
    )
    await query.message.reply_text("Выберите вариант залога:", reply_markup=deposit_keyboard())
    return CHOOSING_DEPOSIT


async def receive_custom_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["duration_text"] = text
    context.user_data["price"] = "уточняется индивидуально"

    await update.message.reply_text(
        f"Длительность: {text}. Точную стоимость согласуем при подтверждении заявки.\n\n"
        "Как оформим залог?",
        reply_markup=deposit_keyboard(),
    )
    return CHOOSING_DEPOSIT


# ---------- Шаг 4: залог ----------

async def choose_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "deposit_money":
        context.user_data["deposit"] = f"{config.DEPOSIT_MONEY}₽"
    else:
        context.user_data["deposit"] = config.DEPOSIT_ALT_TEXT.capitalize()

    await query.edit_message_text(f"Залог: {context.user_data['deposit']}")
    await query.message.reply_text(
        "📞 Оставьте контакт для связи — отправьте номер телефона текстом "
        "или нажмите кнопку ниже.",
        reply_markup=contact_keyboard(),
    )
    return ENTERING_CONTACT


# ---------- Шаг 5: контакт ----------

async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from telegram import ReplyKeyboardRemove

    if update.message.contact:
        contact = update.message.contact.phone_number
    else:
        contact = update.message.text.strip()

    context.user_data["contact"] = contact

    summary = build_summary(update, context)
    await update.message.reply_html(
        f"Проверьте заявку перед отправкой:\n\n{summary}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text("Всё верно?", reply_markup=confirm_keyboard())
    return CONFIRMING


# ---------- Шаг 6: подтверждение и отправка админу ----------

def build_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    d = context.user_data
    user = update.effective_user
    username = f"@{user.username}" if user.username else "(нет username)"
    return (
        f"👤 Клиент: {user.full_name} {username}\n"
        f"🎧 Услуга: {d.get('service_name')}\n"
        f"📅 Дата: {d.get('date')}\n"
        f"⏱ Длительность: {d.get('duration_text')}\n"
        f"💰 Стоимость: {d.get('price')}\n"
        f"🔒 Залог: {d.get('deposit')}\n"
        f"📞 Контакт: {d.get('contact')}\n"
    )


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_no":
        context.user_data.clear()
        await query.edit_message_text("Заявка отменена. Чтобы начать заново — отправьте /start.")
        return ConversationHandler.END

    user = update.effective_user
    d = context.user_data

    app_id = storage.save_application({
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "service": d.get("service_name"),
        "date": d.get("date"),
        "duration": d.get("duration_text"),
        "price": d.get("price"),
        "deposit": d.get("deposit"),
        "contact": d.get("contact"),
    })

    admin_text = (
        f"🆕 <b>Новая заявка #{app_id}</b>\n\n"
        f"{build_summary(update, context)}\n"
        "↩️ Ответьте (Reply) на это сообщение, чтобы написать клиенту напрямую."
    )
    admin_message = await context.bot.send_message(
        chat_id=config.ADMIN_ID, text=admin_text, parse_mode="HTML"
    )
    storage.save_reply_mapping(admin_message.message_id, update.effective_chat.id, user.full_name)

    await query.edit_message_text(
        f"✅ Заявка #{app_id} отправлена! Мы свяжемся с вами для подтверждения встречи."
    )
    context.user_data.clear()
    return ConversationHandler.END
