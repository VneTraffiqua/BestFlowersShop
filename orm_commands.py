import os
import django
from flower_shop_bot.settings import *

os.environ['DJANGO_SETTINGS_MODULE'] = 'bot_settings'
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

django.setup()

from bot.models import (
    Flower,
    Customer,
    Bouquet,
    Order,
    Category
)


def get_all_flowers():
    return [flower.title for flower in Flower.objects.all()]


if __name__ == '__main__':
    print(get_all_flowers())
