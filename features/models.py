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
        max_length=200,
        help_text=_("Identifier for the feature in the source"),
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
        ),
        url=models.URLField(
            verbose_name=_("url"), blank=True, help_text=_("URL of the feature")
        ),
        description=models.TextField(verbose_name=_("description"), blank=True),
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
    tags = models.ManyToManyField("Tag", related_name="features", through="FeatureTag")

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["source_type", "source_id"], name="unique_source_feature"
            ),
        ]

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())

    @property
    def ahti_id(self):
        return f"{self.source_type.system}:{self.source_type.type}:{self.source_id}"


class Image(models.Model):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("feature"),
    )
    url = models.URLField(verbose_name=_("url"), max_length=2000)
    copyright_owner = models.CharField(
        verbose_name=_("copyright owner"), max_length=200
    )
    license = models.ForeignKey(
        "License",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("license"),
    )

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ("id",)

    def __str__(self):
        return self.url


class License(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=200),
    )

    class Meta:
        verbose_name = _("license")
        verbose_name_plural = _("licenses")
        ordering = ("id",)

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())


class Tag(TranslatableModel):
    id = models.CharField(max_length=200, primary_key=True)
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=200),
    )

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ("id",)

    def __str__(self):
        return self.id


class FeatureTag(TimestampedModel):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("feature tag")
        verbose_name_plural = _("feature tags")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["feature", "tag"], name="unique_feature_tag"
            ),
        ]


class ContactInfo(models.Model):
    feature = models.OneToOneField(
        Feature,
        verbose_name=_("feature"),
        related_name="contact_info",
        on_delete=models.CASCADE,
    )
    street_address = models.CharField(
        verbose_name=_("street address"), blank=True, max_length=200
    )
    postal_code = models.CharField(
        verbose_name=_("postal code"), blank=True, max_length=10
    )
    municipality = models.CharField(_("municipality"), max_length=64, blank=True)
    phone_number = models.CharField(
        verbose_name=_("phone number"), max_length=32, blank=True
    )
    email = models.EmailField(verbose_name=_("email"), blank=True)

    class Meta:
        verbose_name = _("contact info")
        verbose_name_plural = _("contact info")
        ordering = ("id",)
