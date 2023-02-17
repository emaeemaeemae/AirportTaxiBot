import logging

import handlers
import config

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler)


# add logger
def start_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # noqa
        level=logging.INFO)


logger = logging.getLogger(__name__)

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_
}


class Bot:

    def __init__(self):
        self.application = ApplicationBuilder(). \
            token(config.TELEGRAM_BOT_TOKEN).build()

        # handlers init
        for command_name, command_handler in COMMAND_HANDLERS.items():
            self.application.add_handler(
                CommandHandler(command_name, command_handler))
        self.application.add_handler(
            handlers.new_drive_conversation())


# run
if __name__ == '__main__':
    start_logging()
    bot = Bot()
    bot.application.run_polling()
