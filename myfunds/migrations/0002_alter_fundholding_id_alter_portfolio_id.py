# Generated by Django 5.1.2 on 2024-12-26 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myfunds", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fundholding",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="portfolio",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
