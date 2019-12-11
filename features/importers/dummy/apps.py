from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DummyConfig(AppConfig):
    name = "features.importers.dummy"
    verbose_name = _("Dummy importer")

    def ready(self):
        from features.importers.registry import importers
        from features.importers.dummy.importer import DummyImporter

        importers.register("dummy", DummyImporter)
