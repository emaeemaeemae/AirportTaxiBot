from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет!\n"
                                        "Я бот, созданный для записи на "
                                        "поездку в такси\n"
                                        "Команды бота:\n"
                                        "/start - приветственное сообщение\n"
                                        "/help - справка\n"
                                        "/new_drive - новая поездка")
