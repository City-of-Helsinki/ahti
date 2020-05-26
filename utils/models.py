from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from graphql import GraphQLError
from parler.managers import TranslatableQuerySet as ParlerTranslatableQuerySet
from parler.models import TranslatableModel as ParlerTranslatableModel


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class TranslatableQuerySet(ParlerTranslatableQuerySet):
    @transaction.atomic
    def create_translatable_object(self, **kwargs):
        translations = kwargs.pop("translations")
        obj = self.create(**kwargs)
        obj.create_or_update_translations(translations)
        return obj


class TranslatableModel(ParlerTranslatableModel):
    objects = TranslatableQuerySet.as_manager()

    class Meta:
        abstract = True

    @transaction.atomic
    def create_or_update_translations(self, translations):
        if settings.PARLER_DEFAULT_LANGUAGE_CODE not in [
            translation["language_code"] for translation in translations
        ]:
            raise GraphQLError(
                f'Default translation "{settings.PARLER_DEFAULT_LANGUAGE_CODE}" '
                f"is missing"
            )
        self.clear_translations()
        for translation in translations:
            language_code = translation.pop("language_code")
            if language_code not in settings.PARLER_SUPPORTED_LANGUAGE_CODES:
                continue
            self.create_translation(language_code=language_code, **translation)

    def clear_translations(self):
        for code in self.get_available_languages():
            self.delete_translation(code)
