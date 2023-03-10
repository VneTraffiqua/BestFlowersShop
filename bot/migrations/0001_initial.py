
# Generated by Django 4.1.5 on 2023-01-18 13:03

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bouquet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('image', models.ImageField(upload_to='', verbose_name='Изображение')),
                ('price', models.IntegerField(verbose_name='Стоимость')),
                ('bouquet_meaning', models.CharField(max_length=255, verbose_name='Смысл букета')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=128, null=True, region='RU', verbose_name='Номер покупателя')),
                ('floral_composition', models.CharField(max_length=255, verbose_name='Цветочная композиция')),
                ('status', models.BooleanField()),

            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Имя')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('delivery_date', models.DateField(verbose_name='Дата доставки')),
                ('delivery_time', models.TimeField(verbose_name='Время доставки')),
            ],
        ),
    ]
