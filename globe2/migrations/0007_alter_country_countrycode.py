# Generated by Django 3.2.12 on 2023-11-15 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('globe2', '0006_alter_country_countrycode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='countryCode',
            field=models.CharField(max_length=10),
        ),
    ]
