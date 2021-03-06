# Generated by Django 3.2.3 on 2022-03-13 13:22

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webscrape', '0003_savedproducts'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrendSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search', models.CharField(max_length=100)),
                ('linK', models.URLField()),
                ('stores', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=8), size=8)),
            ],
        ),
    ]
