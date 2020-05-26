from decimal import Decimal

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from ahti import settings
from features.enums import (
    FeatureDetailsType,
    FeatureTagSource,
    OverrideFieldType,
    Visibility,
    Weekday,
)
from utils.models import TimestampedModel, TranslatableModel, TranslatableQuerySet


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
            verbose_name=_("url"),
            blank=True,
            help_text=_("URL for more information about this feature"),
        ),
        one_liner=models.CharField(
            verbose_name=_("one-liner"),
            max_length=64,
            blank=True,
            help_text=_("A short description limited to 64 chars"),
        ),
        description=models.TextField(
            verbose_name=_("description"),
            blank=True,
            help_text=_("Description of the feature"),
        ),
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
        help_text=_("Category the feature belongs to"),
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


class FeatureDetails(models.Model):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name=_("details"),
    )
    type = models.CharField(
        max_length=6,
        choices=FeatureDetailsType.choices,
        verbose_name=_("type"),
        help_text=_("What type of details are described in this object"),
    )
    data = JSONField(
        verbose_name=_("data"),
        default=dict,
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
    )

    class Meta:
        verbose_name = _("feature details")
        verbose_name_plural = _("feature details")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["feature", "type"], name="unique_feature_detail_type"
            ),
        ]

    def __str__(self):
        return f"{gettext(FeatureDetailsType(self.type).label)}"


class Image(models.Model):
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("feature"),
    )
    url = models.URLField(
        verbose_name=_("url"), max_length=2000, help_text=_("URL of the image")
    )
    copyright_owner = models.CharField(
        verbose_name=_("copyright owner"),
        max_length=200,
        help_text=_("Copyright owner of the image (person)"),
    )
    license = models.ForeignKey(
        "License",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("license"),
        help_text=_("License associated with the image"),
    )

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ("id",)

    def __str__(self):
        return self.url


class License(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            verbose_name=_("name"),
            max_length=200,
            help_text=_("Display name of the license"),
        ),
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
        name=models.CharField(
            verbose_name=_("name"),
            max_length=200,
            help_text=_("Display name of the tag"),
        ),
    )

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ("id",)

    def __str__(self):
        return self.id


class PriceTag(TranslatableModel):
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="price_tags"
    )
    translations = TranslatedFields(
        item=models.CharField(
            max_length=25, verbose_name=_("name"), help_text=_("Name of the item")
        ),
        unit=models.CharField(
            max_length=15,
            verbose_name=_("unit"),
            blank=True,
            help_text=_(
                "Unit of the price (e.g. 'hour', 'day', 'piece', 'person', 'child', "
                "'one way')"
            ),
        ),
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        help_text=_("Price of the item in EUR"),
    )


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


class FeatureTeaser(TranslatableModel):
    feature = models.OneToOneField(
        Feature,
        on_delete=models.CASCADE,
        related_name="teaser",
        verbose_name=_("teaser"),
    )
    translations = TranslatedFields(
        header=models.CharField(
            max_length=64,
            blank=True,
            verbose_name=_("header"),
            help_text=_("An opening, e.g. 'Starting' from 'Starting from 7€/day.'"),
        ),
        main=models.CharField(
            max_length=128,
            blank=True,
            verbose_name=_("main content"),
            help_text=_("The meat of the deal, '7€/day' part"),
        ),
    )

    def __str__(self):
        return f"{self.header} {self.main}"

    class Meta:
        verbose_name = _("teaser")
        verbose_name_plural = _("teasers")
        ordering = ("id",)


class ContactInfo(models.Model):
    feature = models.OneToOneField(
        Feature,
        verbose_name=_("feature"),
        related_name="contact_info",
        on_delete=models.CASCADE,
        help_text=_("Contact information for the given feature"),
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
        comment=models.TextField(
            blank=True,
            verbose_name=_("comment"),
            help_text=_(
                "Comment for this opening hour period (e.g. 'Exceptional opening hours "
                "during Midsummer')"
            ),
        ),
    )

    class Meta:
        verbose_name = _("opening hours period")
        verbose_name_plural = _("opening hours periods")
        ordering = ("id",)

    def __str__(self):
        return ", ".join(
            [str(oh) for oh in self.opening_hours.all().order_by("day", "opens")]
        )


class OpeningHours(models.Model):
    period = models.ForeignKey(
        OpeningHoursPeriod,
        on_delete=models.CASCADE,
        related_name="opening_hours",
        verbose_name=_("opening hours"),
    )
    day = models.IntegerField(choices=Weekday.choices, help_text=_("Day of week"))
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

    def __str__(self):
        if self.all_day:
            hours_string = gettext("all day")
        else:
            opens_string = self.opens.strftime("%H.%M") if self.opens else ""
            closes_string = self.closes.strftime("%H.%M") if self.closes else ""
            hours_string = f"{opens_string}–{closes_string}"
        return f"{gettext(Weekday(self.day).label)}: {hours_string}"


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
