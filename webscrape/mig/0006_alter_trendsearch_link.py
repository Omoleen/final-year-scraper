# Generated by Django 4.0.4 on 2023-02-04 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webscrape', '0005_rename_link_trendsearch_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trendsearch',
            name='link',
            field=models.CharField(max_length=100),
        ),
    ]
