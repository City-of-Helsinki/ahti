from copy import deepcopy

from categories.tests.factories import CategoryFactory
from features.enums import Visibility
from features.models import Feature
from features.tests.factories import TagFactory

CREATE_FEATURE_MUTATION = """
mutation createFeature($input: CreateFeatureMutationInput!) {
  createFeature(input: $input) {
    feature {
      geometry {
        type
        coordinates
      }
      properties {
        source {
          system
          type
        }
        translations {
          languageCode
          name
          description
          url
          oneLiner
        }
        tags {
          id
        }
        category {
          id
        }
        contactInfo {
          phoneNumber
          email
          address {
            streetAddress
            postalCode
            municipality
          }
        }
      }
    }
  }
}
"""
CREATE_FEATURE_VARIABLES = {
    "input": {
        "translations": [
            {
                "languageCode": "FI",
                "name": "Feature name",
                "description": "Feature description",
                "url": "www.url.com",
                "oneLiner": "Feature tagline",
            }
        ],
        "geometry": {"type": "Point", "coordinates": [24.940967, 60.168683]},
        "contactInfo": {
            "streetAddress": "Street 123",
            "postalCode": "00100",
            "municipality": "Helsinki",
            "phoneNumber": "+358501234567",
            "email": "email@example.com",
        },
    }
}


def test_create_feature(snapshot, api_client):
    executed = api_client.execute(
        CREATE_FEATURE_MUTATION, variable_values=CREATE_FEATURE_VARIABLES
    )
    snapshot.assert_match(executed)
    assert Feature.objects.count() == 1


def test_create_feature_sets_source_type(api_client):
    api_client.execute(
        CREATE_FEATURE_MUTATION, variable_values=CREATE_FEATURE_VARIABLES
    )

    feature = Feature.objects.first()
    assert feature.source_type.system == "ahti"
    assert feature.source_type.type == "api"


def test_create_feature_sets_source_id(api_client):
    api_client.execute(
        CREATE_FEATURE_MUTATION, variable_values=CREATE_FEATURE_VARIABLES
    )

    feature = Feature.objects.first()
    assert feature.source_id


def test_create_feature_default_translation_required(api_client):
    variables = deepcopy(CREATE_FEATURE_VARIABLES)
    variables["input"]["translations"][0]["languageCode"] = "EN"

    executed = api_client.execute(CREATE_FEATURE_MUTATION, variable_values=variables)

    assert executed["errors"][0]["message"] == 'Default translation "fi" is missing'


def test_create_feature_set_visibility_to_draft(api_client):
    api_client.execute(
        CREATE_FEATURE_MUTATION, variable_values=CREATE_FEATURE_VARIABLES
    )

    feature = Feature.objects.first()
    assert feature.visibility == Visibility.DRAFT


def test_test_create_feature_can_set_category(api_client):
    category = CategoryFactory()
    variables = deepcopy(CREATE_FEATURE_VARIABLES)
    variables["input"]["categoryId"] = category.id

    api_client.execute(CREATE_FEATURE_MUTATION, variable_values=variables)

    feature = Feature.objects.first()
    assert feature.category_id == category.id


def test_test_create_feature_can_set_tags(api_client):
    tag_1 = TagFactory()
    tag_2 = TagFactory()
    variables = deepcopy(CREATE_FEATURE_VARIABLES)
    variables["input"]["tagIds"] = [tag_1.id, tag_2.id]

    api_client.execute(CREATE_FEATURE_MUTATION, variable_values=variables)

    feature = Feature.objects.first()
    assert tag_1 in feature.tags.all()
    assert tag_2 in feature.tags.all()
