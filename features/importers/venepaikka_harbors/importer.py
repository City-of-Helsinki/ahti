from typing import Iterable

import jmespath
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone

from categories.models import Category
from features.enums import FeatureTagSource
from features.importers.base import FeatureImporterBase
from features.importers.venepaikka_harbors import app_settings
from features.models import ContactInfo, Feature, Image, License, SourceType, Tag

query = """
query Harbors {
  harbors {
    edges {
      node {
        id
        geometry {
          type
          coordinates
        }
        properties {
          name
          imageLink
          imageFile
          streetAddress
          zipCode
          municipality
          phone
          email
          servicemapId
        }
      }
    }
  }
}
"""

feature_expression = jmespath.compile(
    """
data.harbors.edges[*].node.{
    id: id,
    name: properties.name,
    lat: geometry.coordinates[1],
    lon: geometry.coordinates[0],
    address: {
        street_address: properties.streetAddress,
        postal_code: properties.zipCode,
        municipality: properties.municipality
        phone_number: properties.phone
        email: properties.email
    },
    images: [properties.imageFile, properties.imageLink]
    servicemap_id: properties.servicemapId
}
"""
)


class VenepaikkaImporter(FeatureImporterBase):
    source_system = "venepaikka"
    source_type = "harbor"

    servicemap_url = "https://palvelukartta.hel.fi/fi/unit/"
    servicemap_link_type = "servicemap"
    image_copyright_owner = "venepaikat.hel.fi"

    def import_features(self):
        source_type = self.get_source_type()
        client = VenepaikkaHarborsClient()
        harbors = client.fetch_harbors(query=query).json()

        # Category, tag and image license is the same for all harbours
        category, created = Category.objects.language("fi").update_or_create(
            id=app_settings.CATEGORY_CONFIG["id"],
            defaults={"name": app_settings.CATEGORY_CONFIG["name"]},
        )
        tag, created = Tag.objects.language("fi").update_or_create(
            id=app_settings.TAG_CONFIG["id"],
            defaults={"name": app_settings.TAG_CONFIG["name"]},
        )
        image_license = License.objects.translated(
            "fi", name=app_settings.IMAGE_LICENSE
        ).first()
        if not image_license:
            image_license = License.objects.language("fi").create(
                name=app_settings.IMAGE_LICENSE
            )

        for harbor in feature_expression.search(harbors):
            feature = self._import_feature(harbor, source_type)
            self._set_feature_category(feature, category)
            self._set_feature_tag(feature, tag)
            self._import_feature_contact_info(feature, harbor["address"])
            self._import_service_map_url(feature, harbor["servicemap_id"])
            self._import_feature_images(feature, harbor["images"], image_license)

    @staticmethod
    def _import_feature(harbor: dict, st: SourceType) -> Feature:
        values = {
            "name": harbor["name"],
            "mapped_at": timezone.now(),
            "source_modified_at": timezone.now(),
            "geometry": Point(harbor["lon"], harbor["lat"], srid=settings.DEFAULT_SRID),
            "source_type": st,
        }
        feature, created = Feature.objects.language("fi").update_or_create(
            source_type=st, source_id=harbor["id"], defaults=values,
        )
        return feature

    def _set_feature_category(self, feature: Feature, category: Category):
        """Set category for the given Feature.

        Pre-existing categories on features are not updated.
        """
        if category and not feature.category:
            feature.category = category
            Feature.objects.filter(pk=feature.pk).update(category=category)

    def _set_feature_tag(self, feature: Feature, tag: Tag):
        """Set tags for the given feature.

        Manually set tags for a feature are kept.
        """
        feature_tags = [tag] if tag else []

        manually_set_tags = [
            ft.tag
            for ft in feature.feature_tags.filter(
                source=FeatureTagSource.MANUAL
            ).select_related("tag")
        ]
        feature_tags.extend(manually_set_tags)
        feature.tags.set(feature_tags)

    def _import_feature_images(
        self, feature: Feature, images: Iterable[dict], license: License
    ):
        """Imports images for a feature and sets the image license.

        Stale images no longer available in the source are removed.
        """
        processed_images = []
        if not images:
            images = []

        for url in images:
            if not url:
                continue

            Image.objects.update_or_create(
                feature=feature,
                url=url,
                defaults={
                    "copyright_owner": self.image_copyright_owner,
                    "license": license,
                },
            )
            processed_images.append(url)

        # Remove images that are unusable or no longer available in the source
        feature.images.exclude(url__in=processed_images).delete()

    def _import_feature_contact_info(self, feature: Feature, address: dict):
        """Imports contact info for the given feature."""
        if not (
            address["street_address"]
            or address["postal_code"]
            or address["municipality"]
            or address["phone_number"]
            or address["email"]
        ):
            # Delete the contact info if source doesn't provide this information
            if hasattr(feature, "contact_info"):
                feature.contact_info.delete()
        else:
            ContactInfo.objects.update_or_create(
                feature=feature,
                defaults={
                    "street_address": address["street_address"] or "",
                    "postal_code": address["postal_code"] or "",
                    "municipality": address["municipality"] or "",
                    "phone_number": address["phone_number"] or "",
                    "email": address["email"] or "",
                },
            )

    def _import_service_map_url(self, feature: Feature, servicemap_id: str):
        if not servicemap_id:
            feature.links.filter(type=self.servicemap_link_type).delete()
        else:
            feature.links.update_or_create(
                type=self.servicemap_link_type,
                defaults={"url": f"{self.servicemap_url}{servicemap_id}"},
            )


class VenepaikkaHarborsClient:
    url = "https://api.hel.fi/berths/graphql_v2/"
    timeout = 10

    def fetch_harbors(self, query: str) -> requests.Response:
        response = requests.post(self.url, json={"query": query}, timeout=self.timeout)
        response.raise_for_status()
        return response
