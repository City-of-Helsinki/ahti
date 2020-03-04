from django.contrib.gis import admin
from parler.admin import TranslatableAdmin

from features.models import Feature, Image


class ImageInline(admin.TabularInline):
    model = Image
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
    search_fields = ("translations__name", "source_id")
    ordering = ("translations__name",)
    autocomplete_fields = ("category", "parents")

    inlines = (ImageInline,)

    def get_queryset(self, request):
        # Ordering by translated name might cause duplicates in the queryset
        return super().get_queryset(request).distinct()
