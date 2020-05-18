# Generated by Django 2.2.8 on 2020-01-03 13:13

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0004_image_license"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.CharField(max_length=200, primary_key=True, serialize=False),
                ),
            ],
            options={
                "verbose_name": "tag",
                "verbose_name_plural": "tags",
                "ordering": ("id",),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FeatureTag",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "modified_at",
                    models.DateTimeField(auto_now=True, verbose_name="modified at"),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="features.Feature",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="features.Tag"
                    ),
                ),
            ],
            options={
                "verbose_name": "feature tag",
                "verbose_name_plural": "feature tags",
                "ordering": ("id",),
            },
        ),
        migrations.AddField(
            model_name="feature",
            name="tags",
            field=models.ManyToManyField(
                related_name="features",
                through="features.FeatureTag",
                to="features.Tag",
            ),
        ),
        migrations.CreateModel(
            name="TagTranslation",
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
                    "name",
                    models.CharField(
                        max_length=200,
                        verbose_name="name",
                        help_text="Display name of the tag",
                    ),
                ),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="features.Tag",
                    ),
                ),
            ],
            options={
                "verbose_name": "tag Translation",
                "db_table": "features_tag_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name="featuretag",
            constraint=models.UniqueConstraint(
                fields=("feature", "tag"), name="unique_feature_tag"
            ),
        ),
    ]
