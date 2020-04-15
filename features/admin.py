from django.contrib.gis import admin
from django.db.models.functions import Concat
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from features.models import (
    ContactInfo,
    Feature,
    FeatureTag,
    FeatureTeaser,
    Image,
    License,
    Link,
    OpeningHours,
    OpeningHoursPeriod,
    Override,
    PriceTag,
    SourceType,
    Tag,
)


class ContactInfoInline(admin.StackedInline):
    model = ContactInfo


class FeatureTagInline(admin.TabularInline):
    model = FeatureTag
    autocomplete_fields = ("tag",)
    extra = 0


class FeatureTeaserInLine(TranslatableTabularInline):
    model = FeatureTeaser


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0


class OpeningHourInline(admin.TabularInline):
    model = OpeningHours
    extra = 7

    def get_extra(self, request, obj=None, **kwargs):
        return self.extra - obj.opening_hours.count() if obj else self.extra


class OpeningHoursPeriodInline(TranslatableTabularInline):
    model = OpeningHoursPeriod
    show_change_link = True
    extra = 0


class OverrideInline(TranslatableTabularInline):
    model = Override
    extra = 1


class PriceTagInLine(TranslatableTabularInline):
    model = PriceTag
    extra = 0


@admin.register(Feature)
class FeatureAdmin(TranslatableAdmin, admin.OSMGeoAdmin):
    # Helsinki
    default_lon = 2777215
    default_lat = 8434296
    default_zoom = 11

    list_display = (
        "ahti_id",
        "name",
        #    "category",
        "visibility",
        "language_column",
    )
    list_filter = (
        "source_type",
        #    "category",
        "visibility",
        "translations__language_code",
    )
    search_fields = (
        "source_type__system",
        "source_type__type",
        "source_id",
        "translations__name",
    )
    ordering = ("source_type__system", "source_type__type", "source_id")
    # autocomplete_fields = ("category", "parents")
    autocomplete_fields = ("parents",)
    inlines = (
        FeatureTagInline,
        FeatureTeaserInLine,
        ContactInfoInline,
        ImageInline,
        OpeningHoursPeriodInline,
        LinkInline,
        PriceTagInLine,
        OverrideInline,
    )

    def ahti_id(self, obj: Feature):
        return obj.ahti_id

    ahti_id.admin_order_field = Concat(
        "source_type__system", "source_type__type", "source_id"
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("category__translations")


@admin.register(License)
class LicenseAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "language_column",
    )
    search_fields = ("translations__name",)
    list_filter = ("translations__language_code",)


@admin.register(SourceType)
class SourceTypeAdmin(admin.ModelAdmin):
    search_fields = ("system", "type")


@admin.register(OpeningHoursPeriod)
class OpeningHoursPeriodAdmin(TranslatableAdmin):
    list_display = (
        "feature_name",
        "valid_from",
        "valid_to",
        "language_column",
    )
    search_fields = ("feature__translations__name",)
    autocomplete_fields = ("feature",)
    inlines = (OpeningHourInline,)

    def feature_name(self, obj):
        return obj.feature.name

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("feature")
            .prefetch_related("feature__translations")
        )


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "name",
        "language_column",
    )
    search_fields = ("id", "translations__name")
    list_filter = ("translations__language_code",)
