from abc import ABCMeta, abstractmethod
from typing import Optional

from features.models import SourceType, Tag


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


class TagMapper:
    """Maps external tags into Tag instances in the system.

    External tags present in imported sources are either whitelisted,
    mapped into internal tags or ignored. Whitelisted tags are imported
    with their information. Mapped tags are created as internal tags.
    Ignoring means that there are no whitelisting or mapping rules that
    match a given tag so it is not imported. Whitelisting and mapping
    rules are case insensitive.

    Example configuration:
    {
        "rules": [
            {
                # External tags which are mapped into this internal tag
                "mapped_names": ["Swimming", "Beach"],
                "id": "beach",  # Identifier for the internal tag
                "name": "Beach",  # Name of the internal tag
            },
            ...
        ],
        # List of tags which are imported without mapping
        "whitelist": ["Island", "Sauna"],
    }
    """

    internal_tag_prefix = "ahti:tag:"

    def __init__(self, config: dict):
        self.config = {
            "rules": {},
            "whitelist": [item.lower() for item in config.get("whitelist", [])],
        }

        for rule in config.get("rules", []):
            for mapped_name in rule["mapped_names"]:
                self.config[mapped_name.lower()] = rule

    def get_tag(self, tag: dict) -> Optional[Tag]:
        """Return a Tag instance for the given input.

        Tag instance is created or returned if the given input
        matches a Tag recognised by this mapper.

        Expected format for the tag input: {"id": str, "name": str}
        """

        # Whitelisted tags
        if tag["name"].lower() in self.config["whitelist"]:
            tag, created = Tag.objects.language("fi").update_or_create(
                id=tag["id"], defaults={"name": tag["name"]},
            )
            return tag

        # Mapped tags
        mapping = self.config.get(tag["name"].lower())
        if mapping:
            tag, created = Tag.objects.language("fi").update_or_create(
                id=f"{self.internal_tag_prefix}{mapping['id']}",
                defaults={"name": mapping["name"]},
            )
            return tag

        return None
