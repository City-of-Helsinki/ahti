# Generated by Django 3.0.3 on 2020-03-11 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0015_add_feature_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="featuretag",
            name="source",
            field=models.CharField(
                choices=[("MAPPING", "Mapping"), ("MANUAL", "Manual")],
                default="MAPPING",
                help_text="How tag was set for the feature",
                max_length=7,
                verbose_name="source",
            ),
        ),
    ]