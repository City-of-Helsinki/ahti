import pytest

from categories.models import Category
from features.importers.base import CategoryMapper


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mapped_names,expected",
    [
        (["Island"], True),
        (["island"], True),
        (["Archipelago", "Island"], True),
        (["Golf", "Swimming"], False),
    ],
)
def test_category_mapping_rules(mapped_names, expected):
    data = {"id": "matko2:47", "name": "Island"}
    config = {
        "rules": [
            {
                "mapped_names": mapped_names,
                "id": "ahti:category:island",
                "name": "Saaret",
            }
        ],
    }
    mapper = CategoryMapper(config)

    category = mapper.get_category(data)

    if expected:
        assert isinstance(category, Category)
        assert category.id == "ahti:category:island"
        assert category.name == "Saaret"
        assert Category.objects.count() == 1
    else:
        assert category is None
        assert Category.objects.count() == 0
