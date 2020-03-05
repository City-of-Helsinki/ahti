from django.contrib.gis import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from features.models import (
    ContactInfo,
    Feature,
    FeatureTag,
    Image,
    License,
    OpeningHours,
    OpeningHoursPeriod,
    Override,
    Tag,
)


class FeatureTagInline(admin.TabularInline):
    model = FeatureTag
    autocomplete_fields = ("tag",)
    extra = 0


class ContactInfoInline(admin.StackedInline):
    model = ContactInfo


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class OpeningHourInline(admin.TabularInline):
    model = OpeningHours
    min_num = 7
    extra = 0


class OpeningHoursPeriodInline(TranslatableTabularInline):
    model = OpeningHoursPeriod
    show_change_link = True
    extra = 0


class OverrideInline(TranslatableTabularInline):
    model = Override
    extra = 1


@admin.register(Feature)
class FeatureAdmin(TranslatableAdmin, admin.OSMGeoAdmin):
    list_display = (
        "name",
        "category",
        "source_type",
        "source_id",
        "visibility",
        "language_column",
    )
    list_filter = (
        "source_type",
        "category",
        "visibility",
        "translations__language_code",
    )
    search_fields = ("translations__name",)
    ordering = ("translations__name",)
    autocomplete_fields = ("category", "parents")
    inlines = (
        FeatureTagInline,
        ContactInfoInline,
        ImageInline,
        OpeningHoursPeriodInline,
        OverrideInline,
    )

    def get_queryset(self, request):
        # Ordering by translated name might cause duplicates in the queryset
        return super().get_queryset(request).distinct()


@admin.register(License)
class LicenseAdmin(TranslatableAdmin):
    list_display = (
        "name",
        "language_column",
    )
    search_fields = ("translations__name",)
    list_filter = ("translations__language_code",)


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
