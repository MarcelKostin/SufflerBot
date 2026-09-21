from telegram import Update
from telegram.ext import ContextTypes

import config
import storage


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ловит Reply админа на сообщение с заявкой и пересылает текст клиенту."""
    message = update.message
    if not message or not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id
    user_info = storage.get_user_by_admin_message(replied_id)

    if not user_info:
        await message.reply_text(
            "⚠️ Не нашёл клиента для этого сообщения "
            "(возможно, это не заявка, а более старое сообщение)."
        )
        return

    try:
        await context.bot.send_message(
            chat_id=user_info["chat_id"],
            text=message.text,
        )
        await message.reply_text(f"✅ Отправлено клиенту ({user_info['name']}).")
    except Exception as e:  # noqa: BLE001
        await message.reply_text(f"❌ Не удалось отправить: {e}")
