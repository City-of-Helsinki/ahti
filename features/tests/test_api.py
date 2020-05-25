import datetime
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from freezegun import freeze_time
from graphene.test import Client
from graphql_relay import to_global_id

from ahti.schema import schema
from categories.tests.factories import CategoryFactory
from features.enums import HarborMooringType, OverrideFieldType, Visibility, Weekday
from features.models import Feature as FeatureModel
from features.schema import Feature
from features.tests.factories import (
    ContactInfoFactory,
    FeatureFactory,
    FeatureTeaserFactory,
    HarbourFeatureDetailsFactory,
    ImageFactory,
    LinkFactory,
    OpeningHoursFactory,
    OpeningHoursPeriodFactory,
    OverrideFactory,
    PriceTagFactory,
    SourceTypeFactory,
    TagFactory,
)
from utils.pytest import pytest_regex


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
        one_liner="Place X one-liner",
        geometry=Point(24.940967, 60.168683),
        url="https://ahti1.localhost",
    )
    FeatureFactory(
        source_type=st,
        source_id="sid1",
        name="Place Y",
        one_liner="Place Y one-liner",
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
              oneLiner
              url
              ahtiId
              createdAt
              modifiedAt
              translations {
                languageCode
                name
                description
                oneLiner
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


def test_features_visibility(snapshot, api_client):
    FeatureFactory()
    FeatureFactory()

    request = """
    query Features {
      features {
        edges {
          node {
            type
          }
        }
      }
    }
    """
    executed = api_client.execute(request)
    totalFeatures = len(executed["data"]["features"]["edges"])
    f = FeatureModel.objects.last()
    f.visibility = Visibility.HIDDEN
    f.save()
    executed = api_client.execute(request)
    assert len(executed["data"]["features"]["edges"]) == totalFeatures - 1


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
        license__name="Photo license",
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


def test_features_link_query(snapshot, api_client):
    feature = FeatureFactory(name="Feature with external URL",)
    LinkFactory(feature=feature, type="external_url", url="https://example.com")

    executed = api_client.execute(
        """
    query FeatureLinks {
      features {
        edges {
          node {
            properties {
              name
              links {
                type
                url
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


def test_feature_teaser(snapshot, api_client):
    FeatureTeaserFactory()

    executed = api_client.execute(
        """
    query FeatureTeaser {
      features {
        edges {
          node {
            properties {
              teaser {
                header
                main
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


def test_price_list(snapshot, api_client):
    PriceTagFactory(item="Season ticket", price=Decimal("100.01"), unit="a year")
    PriceTagFactory(item="Coffee", price=Decimal("200.01"), unit="")

    executed = api_client.execute(
        """
    query FeaturePriceList {
      features {
        edges {
          node {
            properties {
              details {
                priceList {
                  item
                  price
                  unit
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


def test_feature_harbour_details(snapshot, api_client):
    HarbourFeatureDetailsFactory(
        data__berth_min_depth=2.5,
        data__berth_max_depth=2.5,
        data__berth_moorings=[HarborMooringType.SLIP, HarborMooringType.QUAYSIDE],
    )
    executed = api_client.execute(
        """
    query FeaturesHarborDetails {
      features {
        edges {
          node {
            properties {
              details {
                harbor {
                  moorings
                  depth {
                    min
                    max
                  }
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


def test_feature_with_id(snapshot, api_client):
    st = SourceTypeFactory(system="test", type="test")
    feature = FeatureFactory(source_type=st, source_id="sid0")
    executed = api_client.execute(
        """
    query FeatureWithId {
      feature(id: "%s") {
        properties {
          ahtiId
        }
      }
    }
    """
        % to_global_id(Feature._meta.name, feature.pk)
    )
    snapshot.assert_match(executed)


def test_feature_with_ahti_id(snapshot, api_client):
    st = SourceTypeFactory(system="test", type="test")
    feature = FeatureFactory(source_type=st, source_id="sid0")
    executed = api_client.execute(
        """
    query FeatureWithAhtiId {
      feature(ahtiId: "%s") {
        properties {
          ahtiId
        }
      }
    }
    """
        % feature.ahti_id
    )
    snapshot.assert_match(executed)


def test_feature_query_error(snapshot, api_client):
    executed = api_client.execute(
        """
    query FeatureWithAhtiId {
      feature {
        properties {
          ahtiId
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_tags_query(snapshot, api_client):
    TagFactory(id="tag:1", name="Tag 1")
    TagFactory(id="tag:2", name="Tag 2")

    executed = api_client.execute(
        """
    query Tags {
      tags {
        id
        name
      }
    }
    """
    )
    snapshot.assert_match(executed)


def test_query_features_through_tags_query(snapshot, api_client):
    st = SourceTypeFactory(system="test", type="test")
    feature = FeatureFactory(source_type=st, source_id="sid0")
    feature.tags.add(TagFactory(id="tag:1", name="Tag 1"))

    executed = api_client.execute(
        """
    query TagsAndFeatures {
      tags {
        id
        name
        features {
          edges {
            node {
              properties {
                ahtiId
              }
            }
          }
        }
      }
    }
    """
    )
    snapshot.assert_match(executed)
