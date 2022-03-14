# Generated by Django 3.2.3 on 2022-02-20 11:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webscrape', '0002_delete_savedproducts'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('store', models.CharField(max_length=10)),
                ('link', models.URLField()),
                ('image', models.URLField()),
                ('price', models.FloatField()),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('account', 'link')},
            },
        ),
    ]
