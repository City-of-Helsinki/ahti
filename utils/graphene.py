import django.forms
import django_filters
import graphene
from django.conf import settings
from graphene_django.forms.converter import convert_form_field

LanguageEnum = graphene.Enum(
    "Language", [(lang[0].upper(), lang[0]) for lang in settings.LANGUAGES]
)


def _generate_list_filter_class(inner_type):
    """Generate set of Filter fields that allow using graphene.List types in filtersets.

    From https://github.com/graphql-python/graphene-django/issues/190

    Returns a Filter class that will resolve into a List(`inner_type`) graphene
    type.

    This allows us to do things like use `__in` filters that accept graphene
    lists instead of a comma delimited value string that's interpolated into
    a list by django_filters.BaseCSVFilter (which is used to define
    django_filters.BaseInFilter)
    """

    form_field = type(
        "List{}FormField".format(inner_type.__name__), (django.forms.Field,), {},
    )
    filter_class = type(
        "{}ListFilter".format(inner_type.__name__),
        (django_filters.Filter,),
        {
            "field_class": form_field,
            "__doc__": (
                "{0}ListFilter is a small extension of a raw django_filters.Filter "
                "that allows us to express graphql List({0}) arguments using "
                "FilterSets."
                "Note that the given values are passed directly into queryset filters."
            ).format(inner_type.__name__),
        },
    )
    convert_form_field.register(form_field)(
        lambda x: graphene.List(inner_type, required=x.required)
    )

    return filter_class


StringListFilter = _generate_list_filter_class(graphene.String)
BooleanListFilter = _generate_list_filter_class(graphene.Boolean)
FloatListFilter = _generate_list_filter_class(graphene.Float)
IntListFilter = _generate_list_filter_class(graphene.Int)
UUIDListFilter = _generate_list_filter_class(graphene.UUID)
DateListFilter = _generate_list_filter_class(graphene.Date)
DateTimeListFilter = _generate_list_filter_class(graphene.DateTime)
TimeListFilter = _generate_list_filter_class(graphene.Time)
