# Generated by Django 3.0.2 on 2020-01-20 13:29

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0007_contactinfo"),
    ]

    operations = [
        migrations.CreateModel(
            name="OpeningHoursPeriod",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "valid_from",
                    models.DateField(
                        blank=True,
                        help_text="First day of validity",
                        null=True,
                        verbose_name="valid from",
                    ),
                ),
                (
                    "valid_to",
                    models.DateField(
                        blank=True,
                        help_text="Last day of validity",
                        null=True,
                        verbose_name="valid to",
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opening_hours_periods",
                        to="features.Feature",
                        verbose_name="feature",
                    ),
                ),
            ],
            options={
                "verbose_name": "opening hours period",
                "verbose_name_plural": "opening hours periods",
                "ordering": ("id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="OpeningHours",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day",
                    models.IntegerField(
                        choices=[
                            (1, "Monday"),
                            (2, "Tuesday"),
                            (3, "Wednesday"),
                            (4, "Thursday"),
                            (5, "Friday"),
                            (6, "Saturday"),
                            (7, "Sunday"),
                        ],
                        help_text="Day of week",
                    ),
                ),
                (
                    "opens",
                    models.TimeField(
                        blank=True,
                        help_text="Time of opening",
                        null=True,
                        verbose_name="opens",
                    ),
                ),
                (
                    "closes",
                    models.TimeField(
                        blank=True,
                        help_text="Time of closing",
                        null=True,
                        verbose_name="closes",
                    ),
                ),
                (
                    "all_day",
                    models.BooleanField(
                        default=False, help_text="Open all day", verbose_name="all day"
                    ),
                ),
                (
                    "period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opening_hours",
                        to="features.OpeningHoursPeriod",
                        verbose_name="opening hours",
                    ),
                ),
            ],
            options={
                "verbose_name": "opening hours",
                "verbose_name_plural": "opening hours",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="OpeningHoursPeriodTranslation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language"
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        verbose_name="comment",
                        help_text="Comment for this opening hour period (e.g. "
                        "'Exceptional opening hours during Midsummer')",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="features.OpeningHoursPeriod",
                    ),
                ),
            ],
            options={
                "verbose_name": "opening hours period Translation",
                "db_table": "features_openinghoursperiod_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
