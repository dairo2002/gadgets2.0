# Generated by Django 5.0.3 on 2024-04-01 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0031_alter_ventas_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventas',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='ventas',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
    ]