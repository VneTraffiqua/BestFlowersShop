from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Flower(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Цветы',
        help_text='Введите название цветов'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Цветы'
        verbose_name_plural = 'Цветы'


class Category(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Категория',
        help_text='Введите категорию'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Bouquet(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=255,
        help_text='Введите название'
    )
    category = models.ForeignKey(
        to=Category, on_delete=models.CASCADE, verbose_name='Категория',
    )
    flowers = models.ManyToManyField(
        'Flower',
        verbose_name='Цветы в композиции',
        related_name='flowers'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='media',

    )
    price = models.IntegerField(
        verbose_name='Стоимость'
    )
    bouquet_meaning = models.CharField('Описание', max_length=255)
    status = models.BooleanField()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'


class Order(models.Model):
    address = models.CharField('Адрес', max_length=255)
    delivery_date = models.DateField('Дата доставки', )
    delivery_time = models.TimeField('Время доставки', )
    bouquet = models.ForeignKey(
        to=Bouquet, on_delete=models.CASCADE, verbose_name='Букет>',
    )

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


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

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
