from typing import Type

from features.importers.base import FeatureImporterBase


class ImporterRegistry:
    registry = {}

    def register(self, identifier: str, cls: Type[FeatureImporterBase]):
        """Register a feature importer.

        Registered importer classes will be used when importing features.

        :param identifier: identifier for the importer
        :param cls: Importer class
        """
        assert issubclass(
            cls, FeatureImporterBase
        ), f"Only FeatureImporterBase can be registered, received {cls.__name__}"

        self.registry[identifier] = cls


importers = ImporterRegistry()
