from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Bouquet(models.Model):
    title = models.CharField('Название', max_length=255)
    image = models.ImageField('Изображение')
    price = models.IntegerField('Стоимость')
    bouquet_meaning = models.CharField('Описание', max_length=255)
    status = models.BooleanField()


class Order(models.Model):
    address = models.CharField('Адрес', max_length=255)
    delivery_date = models.DateField('Дата доставки', )
    delivery_time = models.TimeField('Время доставки', )
    bouquet = models.ManyToManyField(
        'Bouquet', blank=True, related_name='bouquets'
    )


class Customer(models.Model):
    name = models.CharField('Имя', max_length=255)
    phone_number = PhoneNumberField(
        region='RU',
        blank=True,
        null=True,
        verbose_name='Номер покупателя',
        db_index=True
    )
    orders = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        verbose_name='Заказы',
        related_name='Orders'
    )
