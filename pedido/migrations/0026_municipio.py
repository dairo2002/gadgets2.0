# Generated by Django 5.0.3 on 2024-03-29 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0025_delete_municipio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.CharField(max_length=10)),
                ('codigo_departamento', models.CharField(max_length=5)),
            ],
        ),
    ]