from django.contrib.gis import admin
from parler.admin import TranslatableAdmin

from features.models import Feature


@admin.register(Feature)
class FeatureAdmin(TranslatableAdmin, admin.OSMGeoAdmin):
    list_display = ("name", "category", "source_type", "source_id")
    list_filter = ("source_type", "category")
    search_fields = ("translations__name", "source_id")
    ordering = ("translations__name",)
    autocomplete_fields = ("category", "parents")
