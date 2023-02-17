from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from config import *


def get_district_keyboard():
    keyboard = [
        [InlineKeyboardButton(d, callback_data=data)]
        for data, d in DISTRICT_DICT.items()
    ]

    return InlineKeyboardMarkup(keyboard)


def get_users_count_keyboard():
    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in range(1, 4)
    ]

    return InlineKeyboardMarkup(keyboard)


def get_max_users_count_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in range(context.user_data['users_count'] + 1, 5)
    ]

    return InlineKeyboardMarkup(keyboard)


def get_class_auto_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(d, callback_data=data)
        ] for data, d in CLASS_DICT.items()
    ]

    return InlineKeyboardMarkup(keyboard)


def get_drives_list_keyboard(context):
    keyboard = [
        [
            InlineKeyboardButton(f"Вариант {i + 1} - "
                                 f"{x['users_count']} из "
                                 f"{x['max_users_count']} человек",
                                 callback_data=x['admin_username'])
        ] for i, x in enumerate(context.user_data['drives_list'])
    ]
    # TODO отмена
    return InlineKeyboardMarkup(keyboard) if keyboard else False


def get_create_drive_keyboard():
    keyboard = [[InlineKeyboardButton(f"Создать новую поездку",
                                      callback_data='new_drive')],
                [InlineKeyboardButton(f"Запустить поиск еще раз",
                                      callback_data='start')]]

    return InlineKeyboardMarkup(keyboard)
