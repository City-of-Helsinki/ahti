from django.contrib import admin
from parler.admin import TranslatableAdmin

from categories.models import Category


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "translations__name")
