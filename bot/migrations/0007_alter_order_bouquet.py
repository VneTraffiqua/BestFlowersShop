# Generated by Django 4.1.5 on 2023-01-23 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_remove_customer_orders_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='bouquet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.bouquet', verbose_name='Букет'),
        ),
    ]
