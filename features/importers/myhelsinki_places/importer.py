import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from features.importers.base import FeatureImporterBase
from features.models import Feature


class MyHelsinkiImporter(FeatureImporterBase):

    feature_id_prefix = "myhelsinki:place:"
    source_system = "myhelsinki.fi"
    source_type = "places"

    def import_features(self):
        st = self.get_source_type()

        mhc = MyHelsinkiPlacesClient()
        places = mhc.fetch_places().json()

        for place in places["data"]:
            values = {
                "name": place["name"]["fi"],
                "url": place["info_url"],
                "mapped_at": timezone.now(),
                "source_modified_at": parse_datetime(place["modified_at"]),
                "geometry": Point(
                    place["location"]["lon"],
                    place["location"]["lat"],
                    srid=settings.DEFAULT_SRID,
                ),
                "source_type": st,
            }

            Feature.objects.language("fi").update_or_create(
                source_id=f"{self.feature_id_prefix}{place['id']}", defaults=values,
            )


class MyHelsinkiPlacesClient:
    tags = ("Island",)  # matko2:47 Island
    base_url = "http://open-api.myhelsinki.fi"
    places_url = "/v1/places/"
    place_url = "/v1/place/{id}"
    main_lang = "fi"
    translation_langs = ("en", "sv")
    timeout = 10

    def fetch_places(self) -> requests.Response:
        params = {
            "language_filter": self.main_lang,
            "tags_search": self.tags,
        }
        headers = {"accept": "application/json"}
        response = requests.get(
            self.base_url + self.places_url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response
