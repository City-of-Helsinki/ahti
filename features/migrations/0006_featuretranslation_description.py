# Generated by Django 2.2.8 on 2020-01-09 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0005_add_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="featuretranslation",
            name="description",
            field=models.TextField(blank=True, verbose_name="description"),
        ),
    ]
