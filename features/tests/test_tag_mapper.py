import pytest

from features.importers.base import TagMapper
from features.models import Tag


@pytest.mark.parametrize(
    "whitelist,expected",
    [
        (["Island"], True),
        (["island"], True),
        (["Swimming", "Island"], True),
        (["Swimming"], False),
    ],
)
def test_tag_mapping_whitelist(whitelist, expected):
    data = {"id": "matko2:47", "name": "Island"}
    config = {"whitelist": whitelist}
    mapper = TagMapper(config)

    tag = mapper.get_tag(data)

    if expected:
        assert isinstance(tag, Tag)
        assert tag.id == "matko2:47"
        assert tag.name == "Island"
        assert Tag.objects.count() == 1
    else:
        assert tag is None
        assert Tag.objects.count() == 0


@pytest.mark.parametrize(
    "mapped_names,expected",
    [
        (["Island"], True),
        (["island"], True),
        (["Archipelago", "Island"], True),
        (["Golf", "Swimming"], False),
    ],
)
def test_tag_mapping_rules(mapped_names, expected):
    data = {"id": "matko2:47", "name": "Island"}
    config = {
        "rules": [
            {"mapped_names": mapped_names, "id": "ahti:tag:island", "name": "saaristo"}
        ],
    }
    mapper = TagMapper(config)

    tag = mapper.get_tag(data)

    if expected:
        assert isinstance(tag, Tag)
        assert tag.id == "ahti:tag:island"
        assert tag.name == "saaristo"
        assert Tag.objects.count() == 1
    else:
        assert tag is None
        assert Tag.objects.count() == 0
