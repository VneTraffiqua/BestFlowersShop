from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
#Hello from Rinat


class Customer(models.Model):
    id = models.IntegerField()
    name = models.CharField('Имя', max_length=255)
    address = models.CharField('Адрес', max_length=255)
    delivery_date = models.DateField('Дата доставки', )
    delivery_time = models.TimeField('Время доставки', )
    bouquet = models.ManyToManyField('Букет', related_name='costomers')


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

