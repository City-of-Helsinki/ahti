import pytest
from graphene.test import Client

from ahti.schema import schema
from categories.tests.factories import CategoryFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def api_client():
    return Client(schema=schema)


def test_feature_categories(snapshot, api_client):
    CategoryFactory(
        id="ahti:category:island", name="Island", description="Island description"
    )
    CategoryFactory(
        id="ahti:category:sauna", name="Sauna", description="Sauna description"
    )

    executed = api_client.execute(
        """
    query FeatureCategories {
      featureCategories {
        id
        name
        description
      }
    }
    """
    )
    snapshot.assert_match(executed)
