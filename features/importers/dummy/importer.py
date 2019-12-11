from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone

from features.importers.base import FeatureImporterBase
from features.models import Feature


class DummyImporter(FeatureImporterBase):

    feature_id_prefix = "dummy:"
    source_system = "Dummy data"
    source_type = "dummy"

    def import_features(self):
        st = self.get_source_type()

        timestamps = {
            "mapped_at": timezone.now(),
            "source_modified_at": timezone.now(),
        }

        # Feature - Kolmen sepän patsas
        feature, created = Feature.objects.language("fi").update_or_create(
            source_id=f"{self.feature_id_prefix}1",
            defaults={
                "name": "Kolmen sepän patsas",
                "geometry": GEOSGeometry(
                    '{"type": "Point", "coordinates": [24.940967, 60.168683]}'
                ),
                "source_type": st,
                **timestamps,
            },
        )

        # Feature - Aleksanteri II patsas
        feature, created = Feature.objects.language("fi").update_or_create(
            source_id=f"{self.feature_id_prefix}2",
            defaults={
                "name": "Aleksanteri II patsas",
                "geometry": GEOSGeometry(
                    '{"type": "Point", "coordinates": [24.952222, 60.169494]}'
                ),
                "source_type": st,
                **timestamps,
            },
        )

        # Ferry - Kauppatori - Vallisaari
        route = GEOSGeometry(
            """{
        "type": "LineString",
        "coordinates": [
            [
              24.954993724822998,
              60.16687219641841
            ],
            [
              24.964499473571777,
              60.163162539707464
            ],
            [
              24.97188091278076,
              60.16153976684021
            ],
            [
              24.981536865234375,
              60.155389584558506
            ],
            [
              24.985570907592773,
              60.15150241760641
            ],
            [
              24.99638557434082,
              60.14902464279283
            ],
            [
              25.00761866569519,
              60.14165429517639
            ],
            [
              25.007221698760983,
              60.140644749393545
            ]
        ]}
        """
        )
        feature, created = Feature.objects.language("fi").update_or_create(
            source_id=f"{self.feature_id_prefix}3",
            defaults={
                "name": "Lautta: Kauppatori - Vallisaari",
                "geometry": route,
                "source_type": st,
                **timestamps,
            },
        )
