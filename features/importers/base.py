from abc import ABCMeta, abstractmethod

from features.models import SourceType


class FeatureImporterBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def source_system(self):
        pass

    @property
    @abstractmethod
    def source_type(self):
        pass

    def get_source_type(self):
        st, created = SourceType.objects.get_or_create(
            system=self.source_system, type=self.source_type
        )
        return st

    @abstractmethod
    def import_features(self):
        """This method should result in data being imported from a source into Features.

        - Creates a features.models.SourceType if one doesn't exists.
        - Creates or updates features.models.Feature instances.
        """
