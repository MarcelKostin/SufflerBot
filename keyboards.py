from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

import config
from states import SERVICE_DAY, SERVICE_HELPER


def services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            f"🎧 Наушник на день — {config.PRICE_DAY}₽",
            callback_data=SERVICE_DAY
        )],
        [InlineKeyboardButton(
            f"🎧+🗣 Наушник с суфлёром — {config.PRICE_HELPER_BASE}₽ "
            f"+ {config.PRICE_HELPER_BLOCK}₽/{config.HELPER_BLOCK_HOURS}ч",
            callback_data=SERVICE_HELPER
        )],
    ]
    return InlineKeyboardMarkup(buttons)


def duration_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for blocks in config.HELPER_DURATION_OPTIONS:
        hours = blocks * config.HELPER_BLOCK_HOURS
        price = config.PRICE_HELPER_BASE + blocks * config.PRICE_HELPER_BLOCK
        label = f"{hours:g} ч — {price}₽"
        buttons.append([InlineKeyboardButton(label, callback_data=f"dur_{blocks}")])
    buttons.append([InlineKeyboardButton("Другая длительность (написать)", callback_data="dur_custom")])
    return InlineKeyboardMarkup(buttons)


def deposit_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"💵 Залог {config.DEPOSIT_MONEY}₽", callback_data="deposit_money")],
        [InlineKeyboardButton(f"🪪 {config.DEPOSIT_ALT_TEXT.capitalize()}", callback_data="deposit_student")],
    ]
    return InlineKeyboardMarkup(buttons)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить мой контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("✅ Отправить заявку", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Отменить", callback_data="confirm_no")],
    ]
    return InlineKeyboardMarkup(buttons)
