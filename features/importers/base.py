from features.models import SourceType


class FeatureImporterBase:

    feature_id_prefix = None
    source_system = None
    source_type = None

    def get_source_type(self):
        st, created = SourceType.objects.get_or_create(
            system=self.source_system, type=self.source_type
        )
        return st

    def import_features(self):
        """This method should result in data being imported from a source into Features.

        - Creates a features.models.SourceType if one doesn't exists.
        - Creates or updates features.models.Feature instances.
        """
        raise NotImplementedError("This needs to be implement in a subclass.")
