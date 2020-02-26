import datetime

import pytest
from django.contrib.gis.geos import Point
from freezegun import freeze_time
from graphene.test import Client
from graphql_relay import to_global_id
from utils.pytest import pytest_regex

from ahti.schema import schema
from categories.tests.factories import CategoryFactory
from features.enums import OverrideFieldType, Weekday
from features.schema import Feature
from features.tests.factories import (
    ContactInfoFactory,
    FeatureFactory,
    ImageFactory,
    OpeningHoursFactory,
    OpeningHoursPeriodFactory,
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


@freeze_time("2019-12-16 12:00:01")
def test_features_query(snapshot, api_client):
    st = SourceTypeFactory(system="test", type="test")
    FeatureFactory(
        source_type=st,
        source_id="sid0",
        name="Place X",
        description="Place X description",
        geometry=Point(24.940967, 60.168683),
        url="https://ahti1.localhost",
    )
    FeatureFactory(
        source_type=st,
        source_id="sid1",
        name="Place Y",
        description="Place Y description",
        geometry=Point(24.952222, 60.169494),
        url="https://ahti2.localhost",
    )

    executed = api_client.execute(
        """
    query Features {
      features {
        edges {
          node {
            type
            geometry {
              type
              coordinates
            }
            properties {
              name
              description
              url
              ahtiId
              createdAt
              modifiedAt
              translations {
                languageCode
                name
                description
                url
              }
              source {
                system
                type
                id
              }
            }
          }
        }
      }
    }
    """
    )

    snapshot.assert_match(executed)


def test_features_query_with_ids(api_client):
    f = FeatureFactory()
    f_node_id = to_global_id(Feature._meta.name, f.pk)

    executed = api_client.execute(
        """
    query FeaturesId {
      features {
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
    assert f_node_id in ids


def test_features_image_query(snapshot, api_client):
    feature = FeatureFactory()
    ImageFactory(
        feature=feature,
        copyright_owner="Photo Grapher",
        url="https://ahti1.localhost/image.png",
    )
    executed = api_client.execute(
        """
    query FeatureImages {
      features {
        edges {
          node {
            properties {
              images {
                url
                copyrightOwner
                license {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_features_tags_query(snapshot, api_client):
    feature = FeatureFactory()
    feature.tags.set(
        [TagFactory(id=f"ahti:{num}", name=f"Tag {num}") for num in range(2)]
    )

    executed = api_client.execute(
        """
    query FeatureImages {
      features {
        edges {
          node {
            properties {
              tags {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_feature_contact_info(snapshot, api_client):
    ContactInfoFactory(
        street_address="Katariinankatu 3",
        postal_code="00170",
        municipality="Helsinki",
        email="ahti@localhost",
        phone_number="+358401234567",
    )

    executed = api_client.execute(
        """
    query FeatureContactInfo {
      features {
        edges {
          node {
            properties {
              contactInfo {
                address {
                  streetAddress
                  postalCode
                  municipality
                }
                email
                phoneNumber
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_feature_opening_hours(snapshot, api_client):
    ohp = OpeningHoursPeriodFactory(
        valid_from=datetime.date(2020, 5, 1),
        valid_to=datetime.date(2020, 8, 31),
        comment="Comment",
    )
    OpeningHoursFactory(
        period=ohp,
        day=Weekday.MONDAY,
        opens=datetime.time(17),
        closes=datetime.time(23),
    )
    OpeningHoursFactory(
        period=ohp, day=Weekday.TUESDAY, opens=None, closes=None, all_day=True
    )

    executed = api_client.execute(
        """
    query FeatureOpeningHours {
      features {
        edges {
          node {
            properties {
              openingHoursPeriods {
                validFrom
                validTo
                comment
                openingHours {
                  day
                  opens
                  closes
                  allDay
                }
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_feature_category(snapshot, api_client):
    category = CategoryFactory(
        id="ahti:category:island", name="Island", description="Island description"
    )
    FeatureFactory(category=category)

    executed = api_client.execute(
        """
    query FeatureCategories {
      features {
        edges {
          node {
            properties {
              category {
                id
                name
                description
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_feature_parents_and_children(snapshot, api_client):
    st = SourceTypeFactory(system="test", type="test")
    f1 = FeatureFactory(source_type=st, source_id="sid0")
    f2 = FeatureFactory(source_type=st, source_id="sid1")
    f2.parents.set([f1])

    executed = api_client.execute(
        """
    query FeatureParents {
      features {
        edges {
          node {
            properties {
              ahtiId
              parents {
                properties {
                  ahtiId
                }
              }
              children {
                properties {
                  ahtiId
                }
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_feature_override_timestamp_is_returned(api_client):
    """API returns the most recent modification timestamp for a feature.

    The source for the value is either the latest override modification
    timestamp or feature's mapping timestamp.
    """
    with freeze_time("2019-12-16 12:00:01"):
        f = FeatureFactory()

    with freeze_time("2020-02-05 12:00:01"):
        OverrideFactory(
            feature=f, field=OverrideFieldType.NAME, string_value="Override"
        )

    executed = api_client.execute(
        """
    query FeaturesOverrideModified {
      features {
        edges {
          node {
            properties {
              modifiedAt
            }
          }
        }
      }
    }
    """
    )

    assert executed["data"]["features"]["edges"][0]["node"]["properties"][
        "modifiedAt"
    ] == pytest_regex(r"2020\-02\-05")


def test_feature_name_override(api_client):
    """API should return the override value instead of the original value."""
    f = FeatureFactory(name="Original name")
    override_name = "Override name"
    OverrideFactory(feature=f, field=OverrideFieldType.NAME, string_value=override_name)

    executed = api_client.execute(
        """
    query FeaturesOverrideName {
      features {
        edges {
          node {
            properties {
              name
            }
          }
        }
      }
    }
    """
    )

    assert (
        executed["data"]["features"]["edges"][0]["node"]["properties"]["name"]
        == override_name
    )


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
