import json
import sys
from pathlib import PurePath
from typing import Mapping


class AppSettings:
    """Overridable app settings.

    Default settings for the app come from a JSON file. Settings can be overridden
    with Django settings.
    """

    def __init__(self, prefix: str, config: Mapping):
        self.prefix = prefix
        self.config = config

    def _setting(self, name, dflt):
        from django.conf import settings

        return getattr(settings, self.prefix + name, dflt)

    @property
    def TAG_CONFIG(self) -> Mapping:
        """Tag configuration.

        Define what static tag to set to features by default.

        Example:
        tag_config = {
            "id": "ahti:tag:harbor",
            "name": "satama",
        }
        """
        return self._setting("TAG_CONFIG", self.config["tag_config"])

    @property
    def CATEGORY_CONFIG(self) -> Mapping:
        """Category configuration.

        Define what static category to set to features by default.

        Example:
        category_config = {
            "id": "ahti:category:harbor",
            "name": "Satamat",
        }
        """
        return self._setting("CATEGORY_CONFIG", self.config["category_config"])

    @property
    def IMAGE_LICENSE(self) -> str:
        """Set the Only images with the given licenses should imported.

        Example:
        image_license = "All rights reserved."
        """
        return self._setting("IMAGE_LICENSE", self.config["image_license"])

    @property
    def MOORING_MAPPING(self) -> Mapping:
        """Mapping of external mooring types into internal ones.

        mooring_mapping = {
            "SINGLE_SLIP_PLACE": "SLIP",
        }
        """
        return self._setting("MOORING_MAPPING", self.config["mooring_mapping"])


path = PurePath(__file__).parent.joinpath("config.json")
with open(path.as_posix(), "r") as f:
    config = json.loads(f.read())

# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html

app_settings = AppSettings("VENEPAIKKA_HARBORS_", config)
app_settings.__name__ = __name__
app_settings.__file__ = __file__
sys.modules[__name__] = app_settings
