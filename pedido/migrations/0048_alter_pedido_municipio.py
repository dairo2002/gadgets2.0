# Generated by Django 5.0.3 on 2024-04-11 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0047_historialpedido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='municipio',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]