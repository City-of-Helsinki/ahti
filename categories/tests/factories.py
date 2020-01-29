import factory

from categories.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    id = factory.Sequence(lambda n: "ahti:category:%d" % n)
    name = factory.Sequence(lambda n: "Category %d" % n)
    description = factory.Sequence(lambda n: "Category %d description" % n)
