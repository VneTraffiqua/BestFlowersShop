import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop_bot.settings")

import django

django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, Bot
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler, PreCheckoutQueryHandler)
from bot.models import Customer, Bouquet
from service_functions import *

BOUQUET_OCCASION, PRICE, ORDER, ADDRESS,  = range(5)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def send_start_msg():

    message = "К какому событию готовимся? Выберите один из вариантов, либо укажите свой."

    return message


def start(update: Update, context: CallbackContext):

    message_keyboard = [['День рождения', 'Свадьба'],
                        ['Без повода']]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    context.user_data['choice'] = 'Событие'

    update.message.reply_text(
        'К какому событию готовимся? Выберите один из вариантов, либо укажите свой.',
        reply_markup=markup,
    )

    return BOUQUET_OCCASION


# def choose_other_occasion(update: Update, context: CallbackContext):
#
#     user_data = context.user_data
#     text = update.message.text
#     category = user_data['choice']
#     user_data[category] = text
#     del user_data['choice']
#
#
#     update.message.reply_text(
#         'Напишите повод'
#     )
#
#     return PRICE


def choose_price(update: Update, context: CallbackContext):

    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    message_keyboard = [
        ['~500', '~1000'],
        ['~2000', 'Больше'],
        ['Не важно']
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    context.user_data['choice'] = 'price'

    update.message.reply_text(
        'На какую сумму рассчитываете?',
        reply_markup=markup,
    )

    return PRICE




def send_bouquet_information(update: Update, context: CallbackContext):

    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    message_keyboard = [
        ['Заказать букет'],
        ['Заказать консультацию', 'Посмотреть всю коллекцию']
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    photo = open('bot/media/boquet.jpg', "rb")

    floral_composition = 'Роза'
    price = 1000

    text = f'''
    Этот букет несет в себе всю нежность ваших чувств и не способен оставить равнодушных ни одного сердца!
    
    Цветочная композиция: {floral_composition}
    
    Стоимость: {price}
    
    Хотите что-то еще более уникальное? Подберите другой букет из нашей коллекции или закажите консультацию флориста

     '''
    bot = Bot(token=TELEGRAM_TOKEN)

    bot.send_photo(
        chat_id=update.message.chat_id,
        photo=photo,
        caption=text,
        reply_markup=markup
    )

    return ORDER


def get_customer_name(update: Update, context: CallbackContext):

    context.user_data['choice'] = 'name'

    update.message.reply_text(
        'Введите ваше имя'
    )

    return ADDRESS


def get_address(update: Update, context: CallbackContext):

    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    context.user_data['choice'] = 'address'




def order_consultation(update: Update, context: CallbackContext):
    pass


def view_full_collection(update: Update, context: CallbackContext):
    pass


def main():
    load_dotenv()
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        allow_reentry=True,
        states={
            BOUQUET_OCCASION: [
                MessageHandler(
                    Filters.regex('^(День рождения|Свадьба|Без повода)$'),
                    choose_price
                ),
                # MessageHandler(
                #     Filters.regex('^Другой повод$'), choose_other_occasion
                # ),
            ],

            PRICE: [MessageHandler(Filters.text, send_bouquet_information)],
            ORDER: [
                MessageHandler(Filters.regex('^Заказать букет'), get_customer_name),
                MessageHandler(Filters.regex('^Заказать консультацию'), order_consultation),
                MessageHandler(Filters.regex('^Посмотреть всю коллекцию'), view_full_collection),
            ],
            ADDRESS: [MessageHandler(Filters.text, get_address)],

        },
        fallbacks=[MessageHandler(Filters.regex('^Стоп$'), start)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
