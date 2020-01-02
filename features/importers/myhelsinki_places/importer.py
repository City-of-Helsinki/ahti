from typing import Iterable

import jmespath
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from features.importers.base import FeatureImporterBase
from features.models import Feature, Image, License, SourceType

feature_expression = jmespath.compile(
    """
data[*].{
    id: id,
    name: name.fi,
    url: info_url,
    modified_at: modified_at,
    lon: location.lon,
    lat: location.lat,
    images: description.images[*].{
        url:url,
        copyright_owner: copyright_holder,
        license: license_type.name
    }
}
"""
)


class MyHelsinkiImporter(FeatureImporterBase):

    source_system = "myhelsinki"
    source_type = "place"

    def import_features(self):
        st = self.get_source_type()

        mhc = MyHelsinkiPlacesClient()
        places = mhc.fetch_places().json()

        for place in feature_expression.search(places):
            feature = self.import_feature(place, st)
            self.import_feature_images(feature, place["images"])

    @staticmethod
    def import_feature(place: dict, st: SourceType) -> Feature:
        values = {
            "name": place["name"],
            "url": place["url"],
            "mapped_at": timezone.now(),
            "source_modified_at": parse_datetime(place["modified_at"]),
            "geometry": Point(place["lon"], place["lat"], srid=settings.DEFAULT_SRID,),
            "source_type": st,
        }
        feature, created = Feature.objects.language("fi").update_or_create(
            source_type=st, source_id=place["id"], defaults=values,
        )
        return feature

    @staticmethod
    def import_feature_images(feature: Feature, images: Iterable[dict]):
        """Imports images for a feature and sets the image license.

        Stale images no longer available in the source are removed.
        """
        if not images:
            images = []

        # Remove images no longer available in the source
        urls = [image["url"] for image in images]
        feature.images.exclude(url__in=urls).delete()

        for image in images:
            url = image["url"]
            copyright_owner = image["copyright_owner"]
            license_name = image["license"]

            license = License.objects.translated("fi", name=license_name).first()
            if not license:
                license = License.objects.language("fi").create(name=license_name)

            Image.objects.get_or_create(
                feature=feature,
                url=url,
                defaults={"copyright_owner": copyright_owner, "license": license},
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
