from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    id = models.CharField(max_length=200, primary_key=True)
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=200),
        description=models.TextField(verbose_name=_("description"), blank=True),
    )

    principle = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = (
            "-principle",
            "translations__name",
        )

    def __str__(self):
        return f'{self.safe_translation_getter("name", super().__str__())}\
                  is principle: {self.principle}'


class CategoriesTable(models.Model):
    feature = models.ForeignKey(
        "features.Feature", null=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    manual = models.BooleanField(default=False, blank=True)
