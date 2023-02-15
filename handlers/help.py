from telegram import Update
from telegram.ext import ContextTypes


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Команды бота:\n"
                                        "/start - приветственное сообщение\n"
                                        "/help - справка\n"
                                        "/new_drive - новая поездка")
