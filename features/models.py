from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFields
from utils.models import TimestampedModel

from ahti import settings
from features.enums import FeatureTagSource, OverrideFieldType, Visibility, Weekday


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
        constraints = [
            models.UniqueConstraint(
                fields=["system", "type"], name="unique_source_type"
            ),
        ]

    def __str__(self):
        return f"{self.system}:{self.type}"


class FeatureQuerySet(TranslatableQuerySet):
    def ahti_id(self, ahti_id: str):
        """Return a single Feature matching the given ahti_id."""
        parts = ahti_id.split(":", 2)
        if len(parts) != 3:
            raise self.model.DoesNotExist(
                f"{self.model._meta.object_name} matching query does not exist."
            )

        return self.get(
            source_type__system=parts[0],
            source_type__type=parts[1],
            source_id=parts[2],
        )


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
        one_liner=models.CharField(
            verbose_name=_("one-liner"),
            max_length=64,
            blank=True,
            help_text=_("A short description limited to 64 chars"),
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
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        related_name="features",
        blank=True,
        null=True,
        verbose_name=_("category"),
    )
    tags = models.ManyToManyField("Tag", related_name="features", through="FeatureTag")
    parents = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="children",
        blank=True,
        verbose_name=_("parents"),
        help_text=_("Parents of this feature (e.g. stops along a route etc.)"),
    )
    visibility = models.SmallIntegerField(
        choices=Visibility.choices, default=Visibility.VISIBLE
    )

    objects = FeatureQuerySet.as_manager()

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


class Link(models.Model):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name=_("feature"),
    )
    type = models.CharField(
        verbose_name=_("type"), max_length=200, help_text=_("Type of the link")
    )
    url = models.URLField(verbose_name=_("url"), max_length=2000)

    def __str__(self):
        return f"{self.type}: {self.url}"

    class Meta:
        verbose_name = _("link")
        verbose_name_plural = _("links")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["feature", "type"], name="unique_link_feature_type"
            ),
        ]


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
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="feature_tags"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="feature_tags")
    source = models.CharField(
        max_length=7,
        choices=FeatureTagSource.choices,
        default=FeatureTagSource.MAPPING,
        verbose_name=_("source"),
        help_text=_("How tag was set for the feature"),
    )

    class Meta:
        verbose_name = _("feature tag")
        verbose_name_plural = _("feature tags")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["feature", "tag"], name="unique_feature_tag"
            ),
        ]

    def __str__(self):
        return f"{self.tag}"


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

    def __str__(self):
        parts = [
            self.street_address,
            self.postal_code,
            self.municipality,
            self.phone_number,
            self.email,
        ]
        return f"{self.feature} - {', '.join(filter(None, parts))}"


class OpeningHoursPeriod(TranslatableModel):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="opening_hours_periods",
        verbose_name=_("feature"),
    )
    valid_from = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("valid from"),
        help_text=_("First day of validity"),
    )
    valid_to = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("valid to"),
        help_text=_("Last day of validity"),
    )
    translations = TranslatedFields(
        comment=models.TextField(blank=True, verbose_name=_("comment")),
    )

    class Meta:
        verbose_name = _("opening hours period")
        verbose_name_plural = _("opening hours periods")
        ordering = ("id",)


class OpeningHours(models.Model):
    period = models.ForeignKey(
        OpeningHoursPeriod,
        on_delete=models.CASCADE,
        related_name="opening_hours",
        verbose_name=_("opening hours"),
    )
    day = models.IntegerField(choices=Weekday.choices)
    opens = models.TimeField(
        blank=True, null=True, verbose_name=_("opens"), help_text=_("Time of opening")
    )
    closes = models.TimeField(
        blank=True, null=True, verbose_name=_("closes"), help_text=_("Time of closing")
    )
    all_day = models.BooleanField(
        default=False, verbose_name=_("all day"), help_text=_("Open all day")
    )

    class Meta:
        verbose_name = _("opening hours")
        verbose_name_plural = _("opening hours")
        ordering = ("id",)


class Override(TranslatableModel, TimestampedModel):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="overrides",
        verbose_name=_("feature"),
    )
    field = models.CharField(
        max_length=4,
        choices=OverrideFieldType.choices,
        verbose_name=_("field"),
        help_text=_("Field that is overridden"),
    )

    translations = TranslatedFields(
        string_value=models.TextField(
            blank=True,
            verbose_name=_("text value"),
            help_text=_("String value for the override"),
        )
    )

    @property
    def value(self):
        if self.field == OverrideFieldType.NAME:
            return self.safe_translation_getter("string_value", "")
        return None

    class Meta:
        verbose_name = _("override")
        verbose_name_plural = _("overrides")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["feature", "field"], name="unique_override_feature_field"
            ),
        ]
