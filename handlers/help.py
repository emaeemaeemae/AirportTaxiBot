from telegram import Update
from telegram.ext import ContextTypes

from templates import render_template
from handlers.response import send_response


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response(
        update,
        context,
        render_template('help.j2')
    )
