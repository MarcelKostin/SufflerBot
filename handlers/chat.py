from telegram import Update
from telegram.ext import ContextTypes

import config
import storage


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пересылает любое текстовое сообщение клиента (вне сценария оформления заявки)
    админу, чтобы переписка о встрече велась прямо в Telegram."""
    message = update.message
    if not message or not message.text:
        return

    user = update.effective_user
    username = f"@{user.username}" if user.username else "(нет username)"

    admin_text = (
        f"✉️ Сообщение от клиента\n"
        f"👤 {user.full_name} {username}\n\n"
        f"{message.text}\n\n"
        "↩️ Ответьте (Reply) на это сообщение, чтобы написать клиенту."
    )
    admin_message = await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_text)
    storage.save_reply_mapping(admin_message.message_id, update.effective_chat.id, user.full_name)
