from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VenepaikkaHarborsConfig(AppConfig):
    name = "features.importers.venepaikka_harbors"
    verbose_name = _("Venepaikka Harbors importer")

    def ready(self):
        from features.importers.registry import importers
        from features.importers.venepaikka_harbors.importer import VenepaikkaImporter

        importers.register("venepaikka_harbors", VenepaikkaImporter)
