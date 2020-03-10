import pytest

from categories.models import Category
from categories.tests.factories import CategoryFactory


@pytest.mark.django_db
def test_category():
    CategoryFactory()

    assert Category.objects.count() == 1
