import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"


DISTRICT_DICT = {'1': 'Приморский',
                 '2': 'Петроградский'}

CLASS_DICT = {'1': 'Эконом',
              '2': 'Комфорт'}
