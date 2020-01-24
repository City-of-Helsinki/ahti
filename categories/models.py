from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    id = models.CharField(max_length=200, primary_key=True)
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=200),
        description=models.TextField(verbose_name=_("description"), blank=True),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ("id",)

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())
