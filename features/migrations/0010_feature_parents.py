# Generated by Django 3.0.2 on 2020-01-29 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0009_feature_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="parents",
            field=models.ManyToManyField(
                help_text="Parents of this feature (e.g. stops along a route etc.)",
                related_name="children",
                to="features.Feature",
                verbose_name="parents",
            ),
        ),
    ]
