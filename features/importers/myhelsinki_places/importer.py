from typing import Iterable

import jmespath
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_time

from features.enums import Weekday
from features.importers.base import CategoryMapper, FeatureImporterBase, TagMapper
from features.models import (
    ContactInfo,
    Feature,
    Image,
    License,
    OpeningHours,
    OpeningHoursPeriod,
    SourceType,
)

feature_expression = jmespath.compile(
    """
data[*].{
    id: id,
    name: name.fi,
    description: description.body,
    url: info_url,
    modified_at: modified_at,
    lon: location.lon,
    lat: location.lat,
    address: {
        street_address: location.address.street_address,
        postal_code: location.address.postal_code
        municipality: location.address.locality
    }
    images: description.images[*].{
        url:url,
        copyright_owner: copyright_holder,
        license: license_type.name
    },
    tags: tags[*].{
        id:id,
        name:name
    }
    opening_hours: {
        hours: opening_hours.hours[*].{
            day: weekday_id,
            opens: opens,
            closes: closes,
            all_day: open24h
        }
        comment: opening_hours.openinghours_exception
    }
}
"""
)


class MyHelsinkiImporter(FeatureImporterBase):

    source_system = "myhelsinki"
    source_type = "place"

    # Query parameters: http://open-api.myhelsinki.fi/doc#/v1places/listAll
    api_calls = [
        {"tags_search": ["Island"]},  # matko2:47 Island
        {"distance_filter": "60.1346, 25.0112, 1.2"},  # Vallisaari
        {"distance_filter": "60.1443, 24.9848, 1"},  # Suomenlinna
    ]

    tag_config = {
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "saaristo"}],
        "whitelist": [],
    }
    category_config = {
        "rules": [{"mapped_names": ["Island"], "id": "island", "name": "Saaret"}],
    }

    def __init__(self):
        super().__init__()
        self.tag_mapper = TagMapper(self.tag_config)
        self.category_mapper = CategoryMapper(self.category_config)

    def import_features(self):
        source_type = self.get_source_type()
        mhc = MyHelsinkiPlacesClient()

        for call_parameters in self.api_calls:
            places = mhc.fetch_places(parameters=call_parameters).json()
            self._process_features(places, source_type)

    def _process_features(self, places: dict, source_type: SourceType):
        for place in feature_expression.search(places):
            feature = self._import_feature(place, source_type)
            self._import_feature_images(feature, place["images"])
            self._import_feature_tags(feature, place["tags"])
            self._import_feature_category(feature, place["tags"])
            self._import_feature_contact_info(feature, place["address"])
            self._import_opening_hours(feature, place["opening_hours"])

    @staticmethod
    def _import_feature(place: dict, st: SourceType) -> Feature:
        values = {
            "name": place["name"],
            "description": place["description"],
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
    def _import_feature_images(feature: Feature, images: Iterable[dict]):
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

    def _import_feature_tags(self, feature: Feature, tags: Iterable[dict]):
        """Imports and sets tags for the given feature."""
        if not tags:
            tags = []
        feature_tags = [tag for tag in map(self.tag_mapper.get_tag, tags) if tag]
        feature.tags.set(feature_tags)

    def _import_feature_category(self, feature: Feature, tags: Iterable[dict]):
        """Imports and set category for the given Feature.

        Categories are mapped based on features tags. Pre-existing
        categories on features are not updated.
        """
        if feature.category:
            return

        for tag in tags:
            category = self.category_mapper.get_category(tag)

            if category:
                feature.category = category
                Feature.objects.filter(pk=feature.pk).update(category=category)

    def _import_feature_contact_info(self, feature: Feature, address: dict):
        """Imports contact info for the given feature."""
        if not (
            address["street_address"]
            or address["postal_code"]
            or address["municipality"]
        ):
            # Delete existing address if source doesn't provide this information
            if hasattr(feature, "contact_info"):
                feature.contact_info.delete()
        else:
            ContactInfo.objects.update_or_create(
                feature=feature,
                defaults={
                    "street_address": address["street_address"] or "",
                    "postal_code": address["postal_code"] or "",
                    "municipality": address["municipality"] or "",
                },
            )

    def _import_opening_hours(self, feature: Feature, opening_hours: dict):
        """Imports opening hours for the given feature."""

        def has_data(hours):
            return bool(hours["opens"] or hours["closes"] or hours["all_day"])

        filtered_hours = (
            filter(has_data, opening_hours["hours"]) if opening_hours["hours"] else []
        )
        hours = list(filtered_hours)

        if opening_hours["comment"] or hours:
            ohps = OpeningHoursPeriod.objects.filter(feature=feature)
            if ohps.count() > 1:
                # MyHelsinki places API provides only one set of opening hours,
                # start from a clean state.
                ohps.delete()

            ohp, created = OpeningHoursPeriod.objects.get_or_create(
                feature=feature, defaults={"comment": opening_hours["comment"]}
            )

            for h in hours:
                day = Weekday(h["day"])
                OpeningHours.objects.get_or_create(
                    period=ohp,
                    day=day,
                    defaults={
                        "opens": parse_time(h["opens"]) if h["opens"] else None,
                        "closes": parse_time(h["closes"]) if h["closes"] else None,
                        "all_day": h["all_day"],
                    },
                )

            # Delete existing opening hours missing from the data
            ohp.opening_hours.exclude(
                day__in=[Weekday(h["day"]) for h in hours]
            ).delete()
        else:
            # Delete any existing opening hours data since its falsy.
            OpeningHoursPeriod.objects.filter(feature=feature).delete()


class MyHelsinkiPlacesClient:
    base_url = "http://open-api.myhelsinki.fi"
    places_url = "/v1/places/"
    place_url = "/v1/place/{id}"
    main_lang = "fi"
    translation_langs = ("en", "sv")
    timeout = 10

    def fetch_places(self, parameters: dict = None) -> requests.Response:
        params = {
            "language_filter": self.main_lang,
        }
        if parameters:
            params.update(parameters)

        headers = {"accept": "application/json"}
        response = requests.get(
            self.base_url + self.places_url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response
