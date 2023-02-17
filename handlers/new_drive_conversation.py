from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler
)

import services as lb
import database as db
from .keyboards import *
from templates import render_template
from handlers.response import send_response

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
    await send_response(
        update,
        context,
        render_template('district.j2'),
        keyboard=get_district_keyboard()
    )

    return DISTRICT


async def district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['district'] = DISTRICT_DICT[update.callback_query.data]

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Выбран район: "
                                             f"{context.user_data['district']}"
                                             f"\n\n")

    await send_response(
        update,
        context,
        render_template('users_count.j2'),
        keyboard=get_users_count_keyboard()
    )

    return NUMBER


async def number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['users_count'] = int(update.callback_query.data)

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Вас поедет "
                                             f"{update.callback_query.data} "
                                             f"человек\n\n")

    await send_response(
        update,
        context,
        render_template('max_users_count.j2'),
        keyboard=get_max_users_count_keyboard(context)
    )

    return MAX_NUMBER


async def max_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['max_users_count'] = int(update.callback_query.data)

    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=update.callback_query.
                                        message.message_id,
                                        text=f"Максимум в авто "
                                             f"{update.callback_query.data} "
                                             f"человек\n\n")

    await send_response(
        update,
        context,
        render_template('class_auto.j2'),
        keyboard=get_class_auto_keyboard()
    )

    return CLASS


async def class_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['class_auto'] = CLASS_DICT[update.callback_query.data]
    context.user_data['drives_list'] = lb.get_drives_list(context)

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
        text=f"Класс авто - {context.user_data['class_auto']}\n")

    r_m = get_drives_list_keyboard(context)

    if r_m:
        await send_response(
            update,
            context,
            render_template('drives_list.j2'),
            keyboard=r_m
        )
    else:
        context.user_data['admin_username'] = \
            update.callback_query.from_user.username

        await send_response(
            update,
            context,
            render_template('empty_drives_list.j2'),
            keyboard=get_create_drive_keyboard()
        )

    return CHOSE_DRIVE


async def chose_drive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == 'new_drive':
        lb.add_new_drive(context)

        await send_response(
            update,
            context,
            render_template('drive_is_created.j2')
        )

        return ConversationHandler.END

    elif update.callback_query.data == 'start':

        await send_response(
            update,
            context,
            render_template('district.j2'),
            keyboard=get_district_keyboard()
        )

        return DISTRICT
    # get admin telegram check drive
    else:
        drive = [x for x in context.user_data['drives_list'] if
                 x['admin_username'] == update.callback_query.data][0]
        try:
            lb.add_users_to_drive(drive, context)
        except db.exceptions_.MySQLWrapperTransactionError:
            await send_response(
                update,
                context,
                render_template('drive_is_not_available.j2')
            )

            context.user_data['drives_list'] = lb.get_drives_list(context)
            r_m = get_drives_list_keyboard(context)
            if r_m:
                await send_response(
                    update,
                    context,
                    render_template('drives_list.j2'),
                    keyboard=r_m
                )
            else:
                context.user_data['admin_username'] = \
                    update.callback_query.from_user.username
                await send_response(
                    update,
                    context,
                    render_template('empty_drives_list.j2'),
                    keyboard=get_create_drive_keyboard()
                )
            return CHOSE_DRIVE

        await send_response(
            update,
            context,
            render_template('registered_to_drive.j2', data={'drive': drive})
        )
        return ConversationHandler.END
