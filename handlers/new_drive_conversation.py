from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler
)

import lib as lb
import database as db
from .config_handlers import *
from .help import help_

DISTRICT, NUMBER, MAX_NUMBER, CLASS, CHOSE_DRIVE, END = range(6)


def new_drive_conversation():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new_drive', new_drive)],
        states={
            DISTRICT: [CallbackQueryHandler(district, pattern=r"^\d+$")],
            NUMBER: [CallbackQueryHandler(number, pattern=r"^\d+$")],
            MAX_NUMBER: [CallbackQueryHandler(max_number, pattern=r"^\d+$")],
            CLASS: [CallbackQueryHandler(class_, pattern=r"^\d+$")],
            CHOSE_DRIVE: [CallbackQueryHandler(chose_drive, pattern=r"^\w+$")]
        },
        fallbacks=[CommandHandler('new_drive', new_drive)],
    )
    return conv_handler


async def new_drive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(d, callback_data=data)]
        for data, d in DISTRICT_DICT.items()
    ]

    r_m = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите район",
                                   reply_markup=r_m)

    return DISTRICT


async def district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['district'] = DISTRICT_DICT[update.callback_query.data]

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Выбран район: "
                                             f"{context.user_data['district']}"
                                             f"\n\n")

    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in range(1, 4)
    ]

    r_m = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Cколько вас?",
                                   reply_markup=r_m)
    return NUMBER


async def number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['users_count'] = int(update.callback_query.data)

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Вас поедет "
                                             f"{update.callback_query.data} "
                                             f"человек\n\n")

    keyboard = [
        [InlineKeyboardButton(str(x), callback_data=str(x))]
        for x in range(context.user_data['users_count'] + 1, 5)
    ]

    r_m = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Максимум в авто",
                                   reply_markup=r_m)
    return MAX_NUMBER


async def max_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['max_users_count'] = int(update.callback_query.data)

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Максимум в авто "
                                             f"{update.callback_query.data} "
                                             f"человек\n\n")

    keyboard = [
        [
            InlineKeyboardButton(d, callback_data=data)
        ] for data, d in CLASS_DICT.items()
    ]

    r_m = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Класс авто",
                                   reply_markup=r_m)
    return CLASS


async def class_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    data['class_auto'] = CLASS_DICT[update.callback_query.data]
    data['tours_list'] = lb.get_tours_list(context)

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Класс авто - "
                                             f"{data['class_auto']}\n")

    keyboard = [
        [
            InlineKeyboardButton(f"Вариант {i + 1} - "
                                 f"{x['users_count']} из "
                                 f"{x['max_users_count']} человек",
                                 callback_data=x['admin_username'])
        ] for i, x in enumerate(data['tours_list'])
    ]
    # TODO отмена
    r_m = InlineKeyboardMarkup(keyboard)

    if keyboard:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Вы выбрали следующую поездку:\n"
                                            f"Район - {data['district']}\n"
                                            f"Класс авто - "
                                            f"{data['class_auto']}\n"
                                            f"Максимум человек в машине - "
                                            f"{data['max_users_count']}\n\n"
                                            f"Подходящие варианты:",
                                       reply_markup=r_m)
    else:
        context.user_data['admin_username'] = \
            update.callback_query.from_user.username
        keyboard = [[InlineKeyboardButton(f"Создать новую поездку",
                                          callback_data='new_drive')],
                    [InlineKeyboardButton(f"Запустить поиск еще раз",
                                          callback_data='start')]]

        r_m = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Подходящих вариантов нет',
                                       reply_markup=r_m)

    return CHOSE_DRIVE


async def chose_drive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    if update.callback_query.data == 'new_drive':
        lb.add_new_drive(context)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Заявка создана, '
                                            'ждите сообщения от попутчиков!')

        await help_(update, context)
        return ConversationHandler.END

    elif update.callback_query.data == 'start':
        return await new_drive(update, context)

    else:
        tour = [x for x in context.user_data['tours_list'] if
                x['admin_username'] == update.callback_query.data][0]
        while True:
            try:
                lb.add_users_to_tour(tour, context)
            except db.exceptions_.MySQLWrapperTransactionError:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text='Ваш вариант уже занят, выберите новый')
                tour = lb.get_tours_list(context)
                if tour:
                    keyboard = [
                        [
                            InlineKeyboardButton(f"Вариант {i + 1} - "
                                                 f"{x['users_count']} из "
                                                 f"{x['max_users_count']} человек",
                                                 callback_data=x[
                                                     'admin_username'])
                        ] for i, x in enumerate(tour)
                    ]
                    # TODO отмена
                    r_m = InlineKeyboardMarkup(keyboard)
                    if keyboard:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"Вы выбрали следующую поездку:\n"
                                 f"Район - {data['district']}\n"
                                 f"Класс авто - "
                                 f"{data['class_auto']}\n"
                                 f"Максимум человек в машине - "
                                 f"{data['max_users_count']}\n\n"
                                 f"Подходящие варианты:",
                            reply_markup=r_m)

                    return CHOSE_DRIVE
                else:
                    context.user_data['admin_username'] = \
                        update.callback_query.from_user.username
                    keyboard = [[InlineKeyboardButton(f"Создать новую поездку",
                                                      callback_data='new_drive')],
                                [InlineKeyboardButton(
                                    f"Запустить поиск еще раз",
                                    callback_data='start')]]

                    r_m = InlineKeyboardMarkup(keyboard)

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text='Подходящих вариантов нет',
                        reply_markup=r_m)
                    break
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Телеграм организатора:\n"
                                                f"@{tour['admin_username']}")
            await help_(update, context)
            break

    # else:
    #     tour = [x for x in context.user_data['tours_list'] if
    #             x['admin_username'] == update.callback_query.data][0]
    #     while True:
    #         try:
    #             lb.add_users_to_tour(tour, context)
    #         except db.exceptions_.MySQLWrapperTransactionError:
    #             await context.bot.send_message(chat_id=update.effective_chat.id,
    #                                            text='Ваш вариант уже занят, выберите новый')
    #             tour = lb.get_tours_list(context)
    #             if tour:
    #                 keyboard = [
    #                     [
    #                         InlineKeyboardButton(f"Вариант {i + 1} - "
    #                                              f"{x['users_count']} из "
    #                                              f"{x['max_users_count']} человек",
    #                                              callback_data=x[
    #                                                  'admin_username'])
    #                     ] for i, x in enumerate(tour)
    #                 ]
    #                 # TODO отмена
    #                 r_m = InlineKeyboardMarkup(keyboard)
    #                 if keyboard:
    #                     await context.bot.send_message(
    #                         chat_id=update.effective_chat.id,
    #                         text=f"Вы выбрали следующую поездку:\n"
    #                              f"Район - {data['district']}\n"
    #                              f"Класс авто - "
    #                              f"{data['class_auto']}\n"
    #                              f"Максимум человек в машине - "
    #                              f"{data['max_users_count']}\n\n"
    #                              f"Подходящие варианты:",
    #                         reply_markup=r_m)
    #
    #                 return CHOSE_DRIVE
    #             else:
    #                 context.user_data['admin_username'] = \
    #                     update.callback_query.from_user.username
    #                 keyboard = [[InlineKeyboardButton(f"Создать новую поездку",
    #                                                   callback_data='new_drive')],
    #                             [InlineKeyboardButton(
    #                                 f"Запустить поиск еще раз",
    #                                 callback_data='start')]]
    #
    #                 r_m = InlineKeyboardMarkup(keyboard)
    #
    #                 await context.bot.send_message(
    #                     chat_id=update.effective_chat.id,
    #                     text='Подходящих вариантов нет',
    #                     reply_markup=r_m)
    #                 break
    #         await context.bot.send_message(chat_id=update.effective_chat.id,
    #                                        text=f"Телеграм организатора:\n"
    #                                             f"@{tour['admin_username']}")
    #         await help_(update, context)
    #         break