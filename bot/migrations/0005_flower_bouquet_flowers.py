# Generated by Django 4.1.5 on 2023-01-19 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_alter_bouquet_options_alter_category_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Введите название цветов', max_length=255, verbose_name='Цветы')),
            ],
            options={
                'verbose_name': 'Цветы',
                'verbose_name_plural': 'Цветы',
            },
        ),
        migrations.AddField(
            model_name='bouquet',
            name='flowers',
            field=models.ManyToManyField(related_name='flowers', to='bot.flower', verbose_name='Цветы в композиции'),
        ),
    ]