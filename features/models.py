from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from utils.models import TimestampedModel

from ahti import settings


class SourceType(models.Model):
    system = models.CharField(
        verbose_name=_("system"),
        max_length=200,
        help_text=_("Name of the source system"),
    )
    type = models.CharField(
        verbose_name=_("type"), max_length=200, help_text=_("Type of the source")
    )

    class Meta:
        verbose_name = _("source type")
        verbose_name_plural = _("source types")
        ordering = ("id",)


class Feature(TranslatableModel, TimestampedModel):
    source_id = models.CharField(
        verbose_name=_("source identifier"),
        unique=True,
        max_length=200,
        help_text=_("Unique identifier indicating the source"),
    )
    source_type = models.ForeignKey(
        SourceType,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("source type"),
    )
    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_("name"), max_length=200, help_text=_("Name of the feature")
        )
    )
    geometry = models.GeometryField(
        verbose_name=_("geometry"),
        srid=settings.DEFAULT_SRID,
        help_text=_("Geometry of the feature"),
    )
    source_modified_at = models.DateTimeField(
        verbose_name=_("source modified at"),
        help_text=_("Time when the feature was modified in the source data"),
    )
    mapped_at = models.DateTimeField(
        verbose_name=_("mapped at"),
        help_text=_(
            "Most recent time when the feature was mapped from the source data"
        ),
    )

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")
        ordering = ("id",)

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())
