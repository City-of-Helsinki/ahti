from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("modified at"), auto_now=True)

    class Meta:
        abstract = True
