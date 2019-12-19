import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_model(user):
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_staff_user(admin_user):
    staff = User.objects.first()
    assert User.objects.count() == 1
    assert staff.is_staff
