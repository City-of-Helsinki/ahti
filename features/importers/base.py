from abc import ABCMeta, abstractmethod
from typing import Optional

from categories.models import Category
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


class MapperBase:
    """Base for implementing a mapper with configuration.

    This base class handles processing the mapping configuration into a structure which
    is faster to search from. Whitelisting configuration can be enabled by a subclass
    with `whitelist` class variable. External strings in whitelisting and mapping rules
    should be treated as case insensitive.

    Example configuration:
    {
        "rules": [
            {
                # External strings which are mapped into an internal object
                "mapped_names": ["Swimming", "Beach"],
                "id": "beach",  # Identifier internal object
                "name": "Beach",  # Name of the internal object
            },
            ...
        ],
        # If whitelisting is enabled
        "whitelist": ["Island", "Sauna"],
    }
    """

    whitelist = False

    def __init__(self, config: dict):
        self.config = {
            "rules": {},
        }

        if self.whitelist:
            self.config["whitelist"] = [
                item.lower() for item in config.get("whitelist", [])
            ]

        for rule in config.get("rules", []):
            for mapped_name in rule["mapped_names"]:
                self.config[mapped_name.lower()] = rule


class TagMapper(MapperBase):
    """Maps external tags into Tag instances in the system.

    External tags present in imported sources are either whitelisted,
    mapped into internal tags or ignored. Whitelisted tags are imported
    with their information. Mapped tags are created as internal tags.
    Only tags defined in the configuration will be considered.
    """

    internal_tag_prefix = "ahti:tag:"
    whitelist = True

    def get_tag(self, tag: dict) -> Optional[Tag]:
        """Return a Tag instance for the given input.

        Tag instance is created and returned if the given input
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


class CategoryMapper(MapperBase):
    """Maps external categories into Category instances in the system.

    External categories present in imported sources are either: mapped
    into internal categories or ignored. Mapped categories are created
    as internal categories. Only categories defined in the configuration
    will be considered.
    """

    internal_category_prefix = "ahti:category:"

    def get_category(self, category: dict) -> Optional[Category]:
        """Return a Category instance for the given input.

        Category instance is created and returned if the given input
        matches a Category recognised by this mapper.

        Expected format for the category input: {"id": str, "name": str}
        """
        mapping = self.config.get(category["name"].lower())
        if mapping:
            category, created = Category.objects.language("fi").update_or_create(
                id=f"{self.internal_category_prefix}{mapping['id']}",
                defaults={"name": mapping["name"]},
            )
            return category
