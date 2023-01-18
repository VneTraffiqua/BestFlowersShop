from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    name = models.CharField('Имя', max_length=255)
    address = models.CharField('Адрес', max_length=255)
    delivery_date = models.DateField('Дата доставки', )
    delivery_time = models.TimeField('Время доставки', )
    bouquet = models.ManyToManyField(
        'Bouquet', blank=True, related_name='bouquets'
    )


class Bouquet(models.Model):
    title = models.CharField('Название', max_length=255)
    image = models.ImageField('Изображение')
    price = models.IntegerField('Стоимость')
    bouquet_meaning = models.CharField('Смысл букета', max_length=255)
    phone_number = PhoneNumberField(
        region='RU',
        blank=True,
        null=True,
        verbose_name='Номер покупателя',
        db_index=True
    )
    floral_composition = models.CharField('Цветочная композиция', max_length=255)
    status = models.BooleanField()

