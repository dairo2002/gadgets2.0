# Generated by Django 5.0.3 on 2024-04-11 05:53

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0046_ventas_cantidad'),
        ('tienda', '0020_alter_categoria_descuento'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pedido.pago')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tienda.producto')),
            ],
        ),
    ]