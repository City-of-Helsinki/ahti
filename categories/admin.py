from django.contrib import admin
from parler.admin import TranslatableAdmin

from categories.models import Category


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("name",)
    search_fields = ("translations__name",)
    ordering = ("translations__name",)
