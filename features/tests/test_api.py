import pytest
from django.contrib.gis.geos import Point
from freezegun import freeze_time
from graphene.test import Client
from graphql_relay import to_global_id

from ahti.schema import schema
from features.schema import Feature
from features.tests.factories import (
    FeatureFactory,
    ImageFactory,
    SourceTypeFactory,
    TagFactory,
)


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
        name="Place X",
        geometry=Point(24.940967, 60.168683),
        url="https://ahti1.localhost",
    )
    FeatureFactory(
        source_type=st,
        name="Place Y",
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
              url
              ahtiId
              createdAt
              modifiedAt
              translations {
                languageCode
                name
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

    assert executed["data"]["features"]["edges"][0]["node"]["id"] == f_node_id


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
