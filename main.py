import os

import telegram

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop_bot.settings")

import django
import phonenumbers
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, Bot
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler, PreCheckoutQueryHandler)
from more_itertools import chunked

from service_functions import *
from bot.models import Customer, Bouquet, Order, Category


BOUQUET_EVENT, OTHER_EVENT, PRICE, FORK, ADDRESS, DELIVERY_DATE, \
    DELIVERY_TIME, PHONE, PHONE_VALIDATOR, FLORIST, VIEWING_COLLECTION, \
    START_OR_STOP, SAVE_DATE, SAVE_TIME, SAVE_ADDRESS = range(15)


def send_start_msg():

    message = "К какому событию готовимся? Выберите один из вариантов, либо укажите свой."
    
    return message


def start(update: Update, context: CallbackContext):


    message_keyboard = \
        chunked([category.title for category in Category.objects.all()], 2)


    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    context.user_data['choice'] = 'event'

    update.message.reply_text(
        'К какому событию готовимся? Выберите один из '
        'вариантов, либо укажите свой.',
        reply_markup=markup,
    )

    return BOUQUET_EVENT


def choose_other_event(update: Update,
                       context: CallbackContext):

    update.message.reply_text(
        'К какому событию хотите подобрать букет?'
    )

    return OTHER_EVENT


def choose_price(update: Update,
                 context: CallbackContext):

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


def send_bouquet_information(update: Update,
                             context: CallbackContext):

    save_user_choice(update, context)

    message_keyboard = [
        ['Заказать букет'],
        [
            'Заказать консультацию',
            'Посмотреть всю коллекцию'
         ]
    ]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    event = context.user_data['event']
    bouquet_set = Bouquet.objects.all()

    if event not in ('Свадьба', 'День рождения', 'В школу', 'Без повода'):
        context.user_data['event'] = event = 'Без повода'

    if event != 'Без повода':    
        if context.user_data['price'] == 'Больше':
            filtered_bouquets_collection = \
                bouquet_set.filter(category__title=event, price__gt=2000)
        elif context.user_data['price'] == '~500':
            filtered_bouquets_collection = \
                bouquet_set.filter(category__title=event, price__lt=500)
        elif context.user_data['price'] == '~1000':
            filtered_bouquets_collection = \
                bouquet_set.filter(category__title=event, price__range=(500, 1000))
        elif context.user_data['price'] == '~2000':
            filtered_bouquets_collection = \
                bouquet_set.filter(category__title=event,price__range=(1000, 2000))
        else:
            filtered_bouquets_collection = bouquet_set.filter(category__title=event)
    else:
        if context.user_data['price'] == 'Больше':
            filtered_bouquets_collection = bouquet_set.filter(price__gt=2000)
        elif context.user_data['price'] == '~500':
            filtered_bouquets_collection = bouquet_set.filter(price__lt=500)
        elif context.user_data['price'] == '~1000':
            filtered_bouquets_collection = bouquet_set.filter(price__range=(500, 1000))
        elif context.user_data['price'] == '~2000':
            filtered_bouquets_collection = bouquet_set.filter(price__range=(1000, 2000))
        else:
            filtered_bouquets_collection = bouquet_set

    context.user_data['filtered_bouquets_collection'] = filtered_bouquets_collection
    context.user_data['bouquet_index'] = 0
    bouquet = filtered_bouquets_collection[context.user_data['bouquet_index']]
    context.user_data['selected_bouquet'] = bouquet

    for bouquet in filtered_bouquets_collection[:5]:
        photo = bouquet.image
        floral_composition = ', '.join([str(flower) for flower in bouquet.flowers.all()])
        price = bouquet.price
        text = f'''
            Название букета: {bouquet.title}
            \n Смысл букета: {bouquet.bouquet_meaning}
            \n Цветочная композиция: {floral_composition}
            \n Стоимость: {price} рублей
            \n Хотите что-то еще более уникальное? Подберите другой букет из нашей коллекции или закажите консультацию флориста
            '''

        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo,
            caption=text,
            reply_markup=markup
        )
        telegram.InlineKeyboardMarkup([['Заказать']], get_customer_name)




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

    message_keyboard = [[
        KeyboardButton('Отправить геопозицию', request_location=True)
    ]]

    markup = ReplyKeyboardMarkup(message_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    update.message.reply_text('Введите ваш адрес', reply_markup=markup)

    return SAVE_ADDRESS


def save_address(update: Update, context: CallbackContext) -> int:

    if update.message.location:
        address = f"{update.message.location['latitude']}, {update.message.location['longitude']}"

    else:
        address = update.message.text

    category = context.user_data['choice']
    context.user_data[category] = address

    return get_delivery_date(update, context)


def generate_date():
    datetime_now = datetime.datetime.now()
    dates_for_button = [[datetime_now.strftime('%d.%m.%Y')]]
    for i in range(2):
        new_list = []
        for k in range(3):
            datetime_now += datetime.timedelta(days=1)
            new_list.append(datetime_now.strftime('%d.%m.%Y'))
        dates_for_button.append(new_list)
    return dates_for_button


def get_delivery_date(update: Update, context: CallbackContext) -> int:
    context.user_data['choice'] = 'delivery_date'

    dates = generate_date()
    message_keyboard = dates
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    update.message.reply_text('Введите дату доставки в формате ДД.ММ.ГГГГ или выберите из предложенных', reply_markup=markup,)
    return SAVE_DATE


def save_date(update, context):
    date = update.message.text
    if not is_valid_date(date):
        update.message.reply_text('Некорректная дата')
        return get_delivery_date(update, context)

    day = date[0:2]
    month = date[3:5]
    year = date[6:]

    date = f'{year}-{month}-{day}'
    category = context.user_data['choice']
    context.user_data[category] = date

    return get_delivery_time(update, context)


def get_delivery_time(update: Update, context: CallbackContext):

    context.user_data['choice'] = 'delivery_time'
    update.message.reply_text('Введите время доставки в формате: ЧЧ.ММ')

    return SAVE_TIME


def save_time(update, context):

    time = update.message.text

    if not is_time_valid(time):
        return get_delivery_time(update, context)

    hours, minutes = map(
        lambda x: f'{int(x):02}',
        time.split(re.search(r'[-.:]{1}', time).group())
    )
    category = context.user_data['choice']
    context.user_data[category] = f'{hours}:{minutes}'
    del context.user_data['choice']

    return get_phonenumber(update, context)


def get_phonenumber(update: Update, context: CallbackContext):

    time = update.message.text

    if not is_time_valid(time):
        update.message.reply_text('Некорректное время')
        return get_delivery_time(update, context)

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
    delivery_date = context.user_data['delivery_date']
    delivery_time = context.user_data['delivery_time']
    bouquet = context.user_data['selected_bouquet']

    customer = Customer.objects.get_or_create(name=name, phone_number=phonenumber)[0]

    Order.objects.create(
        address=address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
        bouquet=bouquet,
        customer=customer
    )

    return start_without_shipping_callback(update, context)


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
    floral_composition = ', '.join([str(flower) for flower in bouquet.flowers.all()])
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
            ['Заказать консультацию']
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


def start_without_shipping_callback(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    title = 'Заказ'
    description = 'Описание платежа'
    payload = 'Custom-Payload'
    provider_token = os.getenv('PAYMENT_TOKEN')
    currency = 'RUB'
    price = context.user_data['selected_bouquet'].price
    prices = [LabeledPrice('Test', price * 100)]

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
    )

    return dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


if __name__ == '__main__':
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        allow_reentry=True,
        states={

            BOUQUET_EVENT: [
                MessageHandler(
                    Filters.regex('^(День рождения|Свадьба|Без повода)$'),
                    choose_price
                ),
                MessageHandler(Filters.regex('^Другой повод'), choose_other_event),
            ],

            OTHER_EVENT: [MessageHandler(Filters.text, choose_price)],

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

            SAVE_ADDRESS: [
                MessageHandler(Filters.text, save_address),
                MessageHandler(Filters.location, save_address),
            ],

            DELIVERY_DATE: [MessageHandler(Filters.text, get_delivery_date)],

            SAVE_DATE: [MessageHandler(Filters.text, save_date)],

            SAVE_TIME: [MessageHandler(Filters.text, save_time)],

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
                MessageHandler(Filters.regex('^Заказать консультацию'), order_consultation)
            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Стоп$'), end)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()


