# Generated by Django 3.0.3 on 2020-03-30 10:35

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0018_featuretranslation_one_liner"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeatureTeaser",
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
                    "feature",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teaser",
                        to="features.Feature",
                        verbose_name="teaser",
                    ),
                ),
            ],
            options={
                "verbose_name": "teaser",
                "verbose_name_plural": "teasers",
                "ordering": ("id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FeatureTeaserTranslation",
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
                    "header",
                    models.CharField(
                        blank=True,
                        help_text="An opening, e.g. 'Starting' from 'Starting from 7€/day.'",
                        max_length=64,
                        verbose_name="header",
                    ),
                ),
                (
                    "main",
                    models.CharField(
                        blank=True,
                        help_text="The meat of the deal, '7€/day' part",
                        max_length=128,
                        verbose_name="main content",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="features.FeatureTeaser",
                    ),
                ),
            ],
            options={
                "verbose_name": "teaser Translation",
                "db_table": "features_featureteaser_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
