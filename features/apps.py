from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FeaturesConfig(AppConfig):
    name = "features"
    verbose_name = _("features")
