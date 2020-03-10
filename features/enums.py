from django.db import models
from django.utils.translation import gettext_lazy as _


class Weekday(models.IntegerChoices):
    """Weekday enum conforms with [iso8601](https://en.wikipedia.org/wiki/ISO_8601)."""

    MONDAY = 1, _("Monday")
    TUESDAY = 2, _("Tuesday")
    WEDNESDAY = 3, _("Wednesday")
    THURSDAY = 4, _("Thursday")
    FRIDAY = 5, _("Friday")
    SATURDAY = 6, _("Saturday")
    SUNDAY = 7, _("Sunday")


class OverrideFieldType(models.TextChoices):
    """Enumeration for overridable fields."""

    NAME = "NAME", _("Name")


class Visibility(models.IntegerChoices):
    """Used to show/hide individual features from the API output"""

    VISIBLE = 1, _("Visible")
    HIDDEN = 0, _("Hidden")
