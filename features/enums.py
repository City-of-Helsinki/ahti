from django.db import models
from django.utils.translation import gettext_lazy as _


class FeatureDetailsType(models.TextChoices):
    HARBOR = "HARBOR", _("Harbor")


class FeatureTagSource(models.TextChoices):
    """Enum for marking how a tag was set for a feature."""

    MAPPING = "MAPPING", _("Mapping")
    MANUAL = "MANUAL", _("Manual")


class HarborMooringType(models.TextChoices):
    """Mooring types which are available in a harbour."""

    # In Finnish: "Aisapaikka"
    SLIP = "SLIP", _("Slip")
    # In Finnish: "Peräpoiju"
    STERN_BUOY = "STERN_BUOY", _("Stern buoy")
    # In Finnish: "Peräpaalu"
    STERN_POLE = "STERN_POLE", _("Stern pole")
    # In Finnish: "Kylki"
    QUAYSIDE = "QUAYSIDE", _("Quayside")
    # In Finnish: "Poiju (merellä)"
    SEA_BUOY = "SEA_BUOY", _("Sea buoy")


class OverrideFieldType(models.TextChoices):
    """Enumeration for overridable fields."""

    NAME = "NAME", _("Name")


class Visibility(models.IntegerChoices):
    """Used to show/hide individual features from the API output."""

    HIDDEN = 0, _("Hidden")
    VISIBLE = 1, _("Visible")
    DRAFT = 2, _("Draft")


class Weekday(models.IntegerChoices):
    """Weekday enum conforms with [iso8601](https://en.wikipedia.org/wiki/ISO_8601)."""

    MONDAY = 1, _("Monday")
    TUESDAY = 2, _("Tuesday")
    WEDNESDAY = 3, _("Wednesday")
    THURSDAY = 4, _("Thursday")
    FRIDAY = 5, _("Friday")
    SATURDAY = 6, _("Saturday")
    SUNDAY = 7, _("Sunday")
