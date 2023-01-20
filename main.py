import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop_bot.settings")

import django
import phonenumbers
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, Bot
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler, PreCheckoutQueryHandler)
from service_functions import *
from bot.models import Customer, Bouquet, Order


BOUQUET_OCCASION, PRICE, FORK, ADDRESS, DELIVERY_TIME, \
    PHONE, PHONE_VALIDATOR, FLORIST, VIEWING_COLLECTION, START_OR_STOP = range(10)

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

    context.user_data['choice'] = 'event'

    update.message.reply_text(
        'К какому событию готовимся? Выберите один из вариантов, либо укажите свой.',
        reply_markup=markup,
    )

    return BOUQUET_OCCASION


def choose_price(update: Update, context: CallbackContext):

    save_user_choice(update, context)

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

    save_user_choice(update, context)

    message_keyboard = [
        ['Заказать букет'],
        ['Заказать консультацию', 'Посмотреть всю коллекцию']
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    event = context.user_data['event']

    if context.user_data['price'] == 'Больше':
        filtered_bouquets_collection = Bouquet.objects.filter(category__title=event,
                                                  price__gt=2000)

    elif context.user_data['price'] == '~500':
        filtered_bouquets_collection = Bouquet.objects.filter(category__title=event,
                                                  price__lt=500)

    elif context.user_data['price'] == '~1000':
        filtered_bouquets_collection = Bouquet.objects.filter(category__title=event,
                                                  price__range=(500, 1000))

    elif context.user_data['price'] == '~2000':
        filtered_bouquets_collection = Bouquet.objects.filter(category__title=event,
                                                  price__range=(1000, 2000))

    else:
        filtered_bouquets_collection = Bouquet.objects.filter(category__title=event)

    context.user_data['filtered_bouquets_collection'] = filtered_bouquets_collection

    context.user_data['bouquet_index'] = 0

    bouquet = filtered_bouquets_collection[context.user_data['bouquet_index']]

    context.user_data['selected_bouquet'] = bouquet

    photo = bouquet.image

    floral_composition = bouquet.floral_composition

    price = bouquet.price

    text = f'''
    {bouquet.title}
    
{bouquet.bouquet_meaning}
    
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

    return FORK


def get_customer_name(update: Update, context: CallbackContext):

    context.user_data['choice'] = 'name'

    update.message.reply_text(
        'Введите ваше имя'
    )

    return ADDRESS


def get_address(update: Update, context: CallbackContext):

    save_user_choice(update, context)

    context.user_data['choice'] = 'address'

    update.message.reply_text(
        'Введите адрес доставки'
    )

    return DELIVERY_TIME


def get_delivery_time(update: Update, context: CallbackContext):

    save_user_choice(update, context)

    context.user_data['choice'] = 'delivery_time'

    update.message.reply_text(
        'Укажите дату и время доставки'
    )

    return PHONE


def get_phonenumber(update: Update, context: CallbackContext):

    save_user_choice(update, context)

    context.user_data['choice'] = 'phonenumber'

    update.message.reply_text(
        'Введите номер телефона'
    )

    return PHONE_VALIDATOR


def validate_phonenumber(update: Update, context: CallbackContext):

    phonenumber = update.message.text

    try:
        pure_phonenumber = phonenumbers.parse(
            phonenumber, 'RU'
        )
    except phonenumbers.phonenumberutil.NumberParseException:
        return enter_number_again(update, context)

    while not phonenumbers.is_valid_number(pure_phonenumber):
        return enter_number_again(update, context)

    if context.user_data.get('name'): # если ввод номера произошел при заказе

        save_user_choice(update, context)

        return save_models(update, context)

    return send_information_to_florist(update, context)


def enter_number_again(update: Update, context: CallbackContext):

    update.message.reply_text(
        '''
Введите корректный номер телефона в международном формате.
Например +79181234567
'''
    )

    return PHONE_VALIDATOR


def save_models(update: Update, context: CallbackContext):

    name = context.user_data['name']
    phonenumber = context.user_data['phonenumber']

    address = context.user_data['address']
    delivery_date = context.user_data['delivery_time'].split()[0]
    delivery_time = context.user_data['delivery_time'].split()[1]
    bouquet = context.user_data['selected_bouquet']

    order = Order.objects.create(
        address=address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )

    order.bouquet.set([bouquet])
    order.save()

    customer = Customer.objects.get_or_create(name=name, phone_number=phonenumber)[0]

    customer.ordedrs = order
    customer.save()

    return send_information_to_courier(update, context)


def order_consultation(update: Update, context: CallbackContext):

    update.message.reply_text(
        'Укажите номер телефона, и наш флорист перезвонит вам в течение 20 минут'
    )

    return PHONE_VALIDATOR


def send_information_to_florist(update: Update, context: CallbackContext):

    context.user_data['choice'] = 'phone_number_to_florist'
    save_user_choice(update, context)


    update.message.reply_text(
        'Флорист скоро свяжется с вами. А пока можете присмотреть что-нибудь из готовой коллекции'
    )

    #Флорист с фиксированным ID получает контакты клиента, кому звонить.

    return view_full_collection(update, context)


def send_information_to_courier(update: Update, context: CallbackContext):

    message_keyboard = [['Стоп', 'Заново']]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    update.message.reply_text(
        text='''Ваш заказ принят, ожидайте доставки

Хотите начать заново?''',
        reply_markup=markup
    )

    return START_OR_STOP

def view_full_collection(update: Update, context: CallbackContext):

    filtered_bouquets_collection = context.user_data['filtered_bouquets_collection']
    if 'bouquet_index' in context.user_data:
        context.user_data['bouquet_index'] += 1

    if context.user_data['bouquet_index'] >= len(filtered_bouquets_collection):
        context.user_data['bouquet_index'] = 0

    index = context.user_data['bouquet_index']

    bouquet = filtered_bouquets_collection[index]
    context.user_data['selected_bouquet'] = bouquet

    photo = bouquet.image
    floral_composition = bouquet.floral_composition
    price = bouquet.price
    text = f'''
    {bouquet.title}
    
{bouquet.bouquet_meaning}
        
Цветочная композиция: {floral_composition}

Стоимость: {price}
        '''

    message_keyboard = [
        ['Заказать букет', 'Другой букет']
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


    bot = Bot(token=TELEGRAM_TOKEN)

    try:
        bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo,
            caption=text,
            reply_markup=markup
        )

        return VIEWING_COLLECTION

    except:

        message_keyboard = [
            ['Стоп', 'Заново'],
        ]

        markup = ReplyKeyboardMarkup(
            message_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        update.message.reply_text(
            text='Вы просмотрели всю коллекцию, хотите начать заново?',
            reply_markup=markup
        )

        return START_OR_STOP

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

            PRICE: [
                MessageHandler(
                    Filters.regex('^(~500|~1000|~2000|Больше|Не важно)$'),
                    send_bouquet_information
                )
            ],

            FORK: [
                MessageHandler(Filters.regex('^Заказать букет'), get_customer_name),
                MessageHandler(Filters.regex('^Заказать консультацию'), order_consultation),
                MessageHandler(Filters.regex('^Посмотреть всю коллекцию'), view_full_collection),
            ],

            ADDRESS: [MessageHandler(Filters.text, get_address)],

            DELIVERY_TIME: [MessageHandler(Filters.text, get_delivery_time)],

            PHONE: [MessageHandler(Filters.text, get_phonenumber)],

            PHONE_VALIDATOR: [MessageHandler(Filters.text, validate_phonenumber)],

            FLORIST: [MessageHandler(Filters.text, send_information_to_florist)],

            VIEWING_COLLECTION: [
                MessageHandler(Filters.regex('^Другой букет'), view_full_collection),
                MessageHandler(Filters.regex('^Заказать букет'), get_customer_name),
            ],

            START_OR_STOP: [
                MessageHandler(Filters.regex('^Заново'), start),
            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Стоп$'), end)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
