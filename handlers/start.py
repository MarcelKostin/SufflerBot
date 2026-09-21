from telegram import Update
from telegram.ext import ContextTypes

import config
from keyboards import services_keyboard
from states import CHOOSING_SERVICE

WELCOME_TEXT = (
    "👋 Здравствуйте! Это аренда микронаушника-суфлёра для театральных постановок, "
    "выступлений и репетиций.\n\n"
    "Доступные варианты:\n\n"
    f"🎧 <b>Наушник на день</b> — {config.PRICE_DAY}₽\n"
    "Вы получаете устройство и самостоятельно им пользуетесь.\n\n"
    f"🎧+🗣 <b>Наушник с суфлёром</b> — {config.PRICE_HELPER_BASE}₽ "
    f"+ {config.PRICE_HELPER_BLOCK}₽ за каждые {config.HELPER_BLOCK_HOURS:g} часа\n"
    "Наш суфлёр подсказывает текст вам в наушник в реальном времени.\n\n"
    f"🔒 <b>Залог:</b> {config.DEPOSIT_MONEY}₽ или {config.DEPOSIT_ALT_TEXT}.\n\n"
    "Выберите услугу, чтобы оформить заявку 👇"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_html(WELCOME_TEXT, reply_markup=services_keyboard())
    return CHOOSING_SERVICE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from telegram.ext import ConversationHandler
    context.user_data.clear()
    await update.message.reply_text(
        "Заявка отменена. Чтобы начать заново — отправьте /start.",
    )
    return ConversationHandler.END
