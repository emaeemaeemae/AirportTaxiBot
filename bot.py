import os
import logging

import handlers

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler)
from dotenv import load_dotenv


# add logger
def start_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # noqa
        level=logging.INFO)


logger = logging.getLogger(__name__)

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
    # "already": handlers.already,
    # "now": handlers.now,
    # "vote": handlers.vote,
    # "cancel": handlers.cancel
}


class Bot:

    def __init__(self):
        self.application = ApplicationBuilder(). \
            token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

        # handlers init
        for command_name, command_handler in COMMAND_HANDLERS.items():
            self.application.add_handler(
                CommandHandler(command_name, command_handler))
        self.application.add_handler(
            handlers.new_drive_conversation())


# run
if __name__ == '__main__':
    load_dotenv()
    start_logging()
    bot = Bot()
    bot.application.run_polling()
