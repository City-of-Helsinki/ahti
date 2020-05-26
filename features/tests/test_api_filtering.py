import pytest
from django.contrib.gis.geos import Point
from freezegun import freeze_time
from graphql_relay import to_global_id

from categories.tests.factories import CategoryFactory
from features.enums import OverrideFieldType
from features.schema import Feature
from features.tests.factories import FeatureFactory, OverrideFactory, TagFactory


def get_response_ids(response):
    return [edge["node"]["id"] for edge in response["data"]["features"]["edges"]]


@pytest.mark.parametrize(
    "geometry,found",
    [
        (Point(24.940967, 60.168683), True),  # Exactly on the spot
        (Point(24.93866, 60.16767), True),  # Within a kilometer
        (Point(24.948333, 60.150833), False),  # Further away
    ],
)
def test_feature_filtering_by_distance(api_client, geometry, found):
    """Filter features that are within a given distance of a geometry."""
    feature = FeatureFactory(geometry=geometry)

    executed = api_client.execute(
        """
    query FeaturesByDistance {
      features(
        distanceLte: {
          geometry:"{'type': 'Point', 'coordinates': [24.940967, 60.168683]}",
          value:1,
          unit:km
        }
      ) {
        edges {
          node {
            id
          }
        }
      }
    }
    """
    )
    ids = get_response_ids(executed)

    if found:
        assert len(ids) == 1
        assert to_global_id(Feature._meta.name, feature.id) in ids
    else:
        assert len(ids) == 0


def test_feature_filtering_updated_since(api_client):
    """Only retrieve Features that have changed since specified timestamp."""
    with freeze_time("2020-02-05 12:00:01"):
        f_old = FeatureFactory(source_id="sid_old")
        f_recent_override = FeatureFactory(source_id="sid_override")
    with freeze_time("2020-02-10 12:00:01"):
        OverrideFactory(
            feature=f_recent_override,
            field=OverrideFieldType.NAME,
            string_value="Override",
        )
        f_recent = FeatureFactory(source_id="sid_recent")
    executed = api_client.execute(
        """
    query FeaturesByTimestamp {
      features(updatedSince: "2020-02-08T12:00:00.0+00:00") {
        edges {
          node {
            id
          }
        }
      }
    }
    """
    )
    ids = get_response_ids(executed)

    assert len(ids) == 2
    assert to_global_id(Feature._meta.name, f_recent.id) in ids
    assert to_global_id(Feature._meta.name, f_recent_override.id) in ids
    assert to_global_id(Feature._meta.name, f_old.id) not in ids


@pytest.mark.parametrize(
    "tag_ids,found",
    [(["first"], True), (["first", "second"], True), (["wrong"], False), ([], False)],
)
def test_feature_filtering_tagged_with_any(api_client, tag_ids, found):
    """Only fetch features tagged with any of the specified tags (ids)."""
    feature = FeatureFactory()
    for tag_id in tag_ids:
        tag = TagFactory(id=tag_id)
        feature.tags.add(tag)

    executed = api_client.execute(
        """
    query FeaturesByTagAny {
      features(taggedWithAny: ["first", "second"]) {
        edges {
          node {
            id
          }
        }
      }
    }
    """
    )
    ids = get_response_ids(executed)

    if found:
        assert len(ids) == 1
        assert to_global_id(Feature._meta.name, feature.id) in ids
    else:
        assert len(ids) == 0


@pytest.mark.parametrize(
    "tag_ids,found",
    [(["first"], False), (["first", "second"], True), (["wrong"], False), ([], False)],
)
def test_feature_filtering_tagged_with_all(api_client, tag_ids, found):
    """Only fetch Features tagged with all of the specified tags (ids)."""
    feature = FeatureFactory()
    for tag_id in tag_ids:
        tag = TagFactory(id=tag_id)
        feature.tags.add(tag)

    executed = api_client.execute(
        """
    query FeaturesByTagAll {
      features(taggedWithAll: ["first", "second"]) {
        edges {
          node {
            id
          }
        }
      }
    }
    """
    )
    ids = get_response_ids(executed)

    if found:
        assert len(ids) == 1
        assert to_global_id(Feature._meta.name, feature.id) in ids
    else:
        assert len(ids) == 0


@pytest.mark.parametrize(
    "category_id,found",
    [("first", True), ("second", True), ("wrong", False), (None, False)],
)
def test_feature_filtering_category(api_client, category_id, found):
    """Only fetch Features from included categories."""
    category = CategoryFactory(id=category_id) if category_id else None
    feature = FeatureFactory(category=category)

    executed = api_client.execute(
        """
    query FeaturesByCategory {
      features(category: ["first", "second"]) {
        edges {
          node {
            id
          }
        }
      }
    }
    """
    )
    ids = get_response_ids(executed)

    if found:
        assert len(ids) == 1
        assert to_global_id(Feature._meta.name, feature.id) in ids
    else:
        assert len(ids) == 0
