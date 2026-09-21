import logging

from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters,
)

import config
from states import CHOOSING_SERVICE, ENTERING_DATE, CHOOSING_DURATION, CHOOSING_DEPOSIT, ENTERING_CONTACT, CONFIRMING
from handlers.start import start, cancel
from handlers.rental import (
    choose_service, receive_date, choose_duration, receive_custom_duration,
    choose_deposit, receive_contact, confirm,
)
from handlers.admin import admin_reply

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def build_application() -> Application:
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    rental_conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_SERVICE: [
                CallbackQueryHandler(choose_service, pattern="^service_"),
            ],
            ENTERING_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date),
            ],
            CHOOSING_DURATION: [
                CallbackQueryHandler(choose_duration, pattern="^dur_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_duration),
            ],
            CHOOSING_DEPOSIT: [
                CallbackQueryHandler(choose_deposit, pattern="^deposit_"),
            ],
            ENTERING_CONTACT: [
                MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, receive_contact),
            ],
            CONFIRMING: [
                CallbackQueryHandler(confirm, pattern="^confirm_"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(rental_conversation)

    # Reply админа в личном чате с ботом -> пересылка клиенту.
    # Работает только в чате самого админа, чтобы случайный Reply клиента
    # не пытался что-то пересылать.
    application.add_handler(
        MessageHandler(
            filters.REPLY & filters.Chat(chat_id=config.ADMIN_ID) & filters.TEXT & ~filters.COMMAND,
            admin_reply,
        )
    )

    return application


def main() -> None:
    application = build_application()
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
