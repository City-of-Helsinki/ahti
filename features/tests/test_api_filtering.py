import pytest
from django.contrib.gis.geos import Point
from freezegun import freeze_time
from graphene.test import Client
from graphql_relay import to_global_id

from ahti.schema import schema
from features.enums import OverrideFieldType
from features.schema import Feature
from features.tests.factories import (
    FeatureFactory,
    OverrideFactory,
    SourceTypeFactory,
    TagFactory,
)


def get_response_ids(response):
    return [edge["node"]["id"] for edge in response["data"]["features"]["edges"]]


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def api_client():
    return Client(schema=schema)


def test_feature_filtering_by_distance(api_client):
    """Filter features that are withing a given distance of a geometry."""
    st = SourceTypeFactory(system="test", type="test")
    f = FeatureFactory(
        source_type=st, source_id="sid0", geometry=Point(24.940967, 60.168683),
    )
    f_within_kilometer = FeatureFactory(
        source_type=st, source_id="sid1", geometry=Point(24.93866, 60.16767),
    )
    f_further_away = FeatureFactory(
        source_type=st, source_id="sid2", geometry=Point(24.948333, 60.150833),
    )
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

    assert to_global_id(Feature._meta.name, f.id) in ids
    assert to_global_id(Feature._meta.name, f_within_kilometer.id) in ids
    assert to_global_id(Feature._meta.name, f_further_away.id) not in ids


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

    assert to_global_id(Feature._meta.name, f_recent.id) in ids
    assert to_global_id(Feature._meta.name, f_recent_override.id) in ids
    assert to_global_id(Feature._meta.name, f_old.id) not in ids


def test_feature_filtering_tagged_with_any(api_client):
    """Only fetch features tagged with any of the specified tags (ids)."""
    t1 = TagFactory(id="first")
    t2 = TagFactory(id="second")
    t_wrong = TagFactory()

    feature_one_tag = FeatureFactory()
    feature_two_tags = FeatureFactory()
    feature_wrong_tags = FeatureFactory()
    feature_no_tags = FeatureFactory()

    feature_one_tag.tags.set([t1])
    feature_two_tags.tags.set([t1, t2])
    feature_wrong_tags.tags.set([t_wrong])

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

    assert len(ids) == 2
    assert to_global_id(Feature._meta.name, feature_one_tag.id) in ids
    assert to_global_id(Feature._meta.name, feature_two_tags.id) in ids
    assert to_global_id(Feature._meta.name, feature_wrong_tags.id) not in ids
    assert to_global_id(Feature._meta.name, feature_no_tags.id) not in ids


def test_feature_filtering_tagged_with_all(api_client):
    """Only fetch Features tagged with all of the specified tags (ids)."""
    t1 = TagFactory(id="first")
    t2 = TagFactory(id="second")
    t_wrong = TagFactory()

    feature_one_tag = FeatureFactory()
    feature_two_tags = FeatureFactory()
    feature_wrong_tags = FeatureFactory()
    feature_no_tags = FeatureFactory()

    feature_one_tag.tags.set([t1])
    feature_two_tags.tags.set([t1, t2])
    feature_wrong_tags.tags.set([t_wrong])

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

    assert len(ids) == 1
    assert to_global_id(Feature._meta.name, feature_one_tag.id) not in ids
    assert to_global_id(Feature._meta.name, feature_two_tags.id) in ids
    assert to_global_id(Feature._meta.name, feature_wrong_tags.id) not in ids
    assert to_global_id(Feature._meta.name, feature_no_tags.id) not in ids
