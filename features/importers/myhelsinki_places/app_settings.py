import sys
from typing import Iterable, Mapping

from utils.utils import read_json_file


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
    def API_CALLS(self) -> Iterable[Mapping]:
        """Calls and parameters which will be sent to the API.

        Query parameters: http://open-api.myhelsinki.fi/doc#/v1places/listAll

        Example:
        api_calls = [
            {"tags_search": ["Island"]},  # matko2:47 Island
            {"distance_filter": "60.1443, 24.9848, 1"},  # Suomenlinna
        ]
        """
        return self._setting("API_CALLS", self.config["api_calls"])

    @property
    def ADDITIONAL_LANGUAGES(self) -> Iterable[str]:
        """Additional languages to import besides Finnish (`fi`).

        Example:
        additional_languages = ["en", "sv"]
        """
        return self._setting(
            "ADDITIONAL_LANGUAGES", self.config["additional_languages"]
        )

    @property
    def TAG_CONFIG(self) -> Mapping:
        """Tag mapping configuration.

        Define how external tags are mapped into internal tags using
        mapping and whitelisting rules.

        Example:
        tag_config = {
            "rules": [
                {
                    "mapped_names": ["Island"],
                    "id": "ahti:tag:island",
                    "name": "saaristo"
                },
            ],
            "whitelist": [],
        }
        """
        return self._setting("TAG_CONFIG", self.config["tag_config"])

    @property
    def CATEGORY_CONFIG(self) -> Mapping:
        """Category mapping configuration.

        Define how imported features are mapped into categories.

        Example:
        category_config = {
            "rules": [
                {
                    "mapped_names": ["Island"],
                    "id": "ahti:category:island",
                    "name": "Saaret",
                },
            ],
        }
        """
        return self._setting("CATEGORY_CONFIG", self.config["category_config"])

    @property
    def ALLOWED_IMAGE_LICENSES(self) -> Iterable[str]:
        """Only images with the given licenses should imported.

        Example:
        allowed_image_licenses = ["All rights reserved.", "MyHelsinki license type A"]
        """
        return self._setting(
            "ALLOWED_IMAGE_LICENSES", self.config["allowed_image_licenses"]
        )


config = read_json_file(__file__, "config.json")

# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html

app_settings = AppSettings("MYHELSINKI_PLACES_", config)
app_settings.__name__ = __name__
app_settings.__file__ = __file__
sys.modules[__name__] = app_settings
