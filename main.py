from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bot import parser, top
from config import bot_token


# Обработка команды /Сервер и сообщения "Сервер"
def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.strip().lower() 
    result = None
    if user_text in ["сервер", "server"]:
        result = parser()
         
    elif user_text == "top":
        result = top()
         
    if not result:
        return

    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            update.message.reply_text(result[i:i+4000])
    else:
        update.message.reply_text(result)

def main():
    # Вставь сюда свой реальный токен Telegram-бота
    TOKEN = bot_token

    # Настройка бота
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Добавляем обработчики
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск
    updater.start_polling()
    print("🤖 Бот запущен. Ожидаем сообщения.")
    updater.idle()

if __name__ == "__main__":
    main()
