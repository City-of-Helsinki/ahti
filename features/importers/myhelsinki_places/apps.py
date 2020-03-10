from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MyHelsinkiPlacesConfig(AppConfig):
    name = "features.importers.myhelsinki_places"
    verbose_name = _("MyHelsinki Places importer")

    def ready(self):
        from features.importers.registry import importers
        from features.importers.myhelsinki_places.importer import MyHelsinkiImporter

        importers.register("myhelsinki_places", MyHelsinkiImporter)
