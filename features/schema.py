import django_filters
import graphene
import graphql_geojson
from django.apps import apps
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from graphene import ID, ObjectType, relay, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_geojson.filters import DistanceFilter
from utils.graphene import StringListFilter

from features import models
from features.enums import HarborMooringType, OverrideFieldType, Visibility, Weekday

HarborMooringTypeEnum = graphene.Enum.from_enum(
    HarborMooringType, description=lambda e: e.label if e else ""
)

WeekdayEnum = graphene.Enum.from_enum(
    Weekday, description=lambda e: e.label if e else ""
)


class Address(ObjectType):
    street_address = graphene.String()
    postal_code = graphene.String()
    municipality = graphene.String()


class ContactInfo(DjangoObjectType):
    """Contact information for the given feature."""

    class Meta:
        model = models.ContactInfo
        fields = ("email", "phone_number")

    address = graphene.Field(Address)

    def resolve_address(self: models.ContactInfo, info, **kwargs):
        return {
            "street_address": self.street_address,
            "postal_code": self.postal_code,
            "municipality": self.municipality,
        }


class ExternalLink(DjangoObjectType):
    """Link to an external system.

    Link can be e.g. to an online store, a berth rental or to ferry information.
    """

    class Meta:
        model = models.Link
        fields = (
            "type",
            "url",
        )


class FeatureSource(ObjectType):
    """Source system information for a feature."""

    system = graphene.String(
        required=True,
        description=_(
            "Name of the source system (e.g. 'myhelsinki', 'ahti', "
            "'ulkoliikuntakartta', 'digitransit')"
        ),
    )
    type = graphene.String(
        required=True,
        description=_(
            "Type of the feature in the source system, if applicable (e.g. 'place', "
            "'activity', 'event', 'route')"
        ),
    )
    id = graphene.String(
        required=True, description="ID of the current feature in source system"
    )


class PriceTag(DjangoObjectType):
    """An item displayed in a price list."""

    class Meta:
        model = models.PriceTag
        fields = ("price",)

    item = graphene.String(required=True, description=_("Name of the item"))
    price = graphene.Decimal(required=True, description=_("Price of the item in EUR"))
    unit = graphene.String(
        description=_(
            "Unit of the price (e.g. 'hour', 'day', 'piece', 'person', 'child', "
            "'one way')"
        ),
    )


class Teaser(DjangoObjectType):
    """Simple content element (e.g. something special about a feature)."""

    class Meta:
        model = models.FeatureTeaser

    header = graphene.String(
        description=_("An opening, e.g. 'Starting' from 'Starting from 7€/day.'")
    )
    main = graphene.String(description=_("The meat of the deal, '7€/day' part"))


class FeatureTranslations(DjangoObjectType):
    "Values in other languages for the feature attributes that can have translations."

    class Meta:
        model = apps.get_model("features", "FeatureTranslation")
        exclude = ("id", "master")


class Image(DjangoObjectType):
    class Meta:
        model = models.Image
        fields = (
            "url",
            "copyright_owner",
            "license",
        )


class License(DjangoObjectType):
    class Meta:
        model = models.License
        fields = ("id",)

    name = graphene.String(required=True, description=_("Display name of the license"))


class Tag(DjangoObjectType):
    """Tags are associated with things (like features)."""

    class Meta:
        model = models.Tag
        fields = ("id", "features")

    name = graphene.String(required=True, description=_("Display name of the tag"))


class OpeningHoursPeriod(DjangoObjectType):
    """A period during which certain opening hours are valid."""

    class Meta:
        model = models.OpeningHoursPeriod
        fields = (
            "valid_from",
            "valid_to",
            "opening_hours",
        )

    comment = graphene.String(
        description=_(
            "Comment for this opening hour period (e.g. 'Exceptional opening hours "
            "during Midsummer')"
        ),
    )


class OpeningHours(DjangoObjectType):
    """The daily opening hours / hours of operation of something."""

    class Meta:
        model = models.OpeningHours
        fields = (
            "opens",
            "closes",
            "all_day",
        )

    day = WeekdayEnum(required=True, description=_("Day of week"))


class Depth(ObjectType):
    """The depth of something, in meters.

    Can be a single value (min and max are equal) or a range.
    (Consider: harbor/lake/pool/mineshaft)."
    """

    min = graphene.Float(
        required=True,
        description=_(
            "An approximation of the minimum depth (or lower end of the range)"
        ),
    )
    max = graphene.Float(
        required=True,
        description=_(
            "An approximation of the maximum depth (or deeper end of the range)"
        ),
    )


class HarborDetails(ObjectType):
    """Information specific to harbors (and piers)."""

    moorings = graphene.List(
        graphene.NonNull(HarborMooringTypeEnum),
        description=_("Mooring types available in the harbor"),
    )
    depth = graphene.Field(
        Depth, description=_("Approximate depth of the harbor, in meters")
    )

    def resolve_moorings(self: models.FeatureDetails, info, **kwargs):
        return self.data["berth_moorings"]

    def resolve_depth(self: models.FeatureDetails, info, **kwargs):
        """Minimum depth is mandatory, maximum is included for a range."""
        min = self.data.get("berth_min_depth")
        max = self.data.get("berth_max_depth")

        if min is None:
            return None

        return {
            "min": min,
            "max": max,
        }


class FeatureDetails(ObjectType):
    """Detailed information a feature might have."""

    harbor = graphene.Field(HarborDetails, description=_("Details of a harbor"))
    price_list = graphene.List(
        "features.schema.PriceTag",
        required=True,
        description=_("Price list related to a feature"),
    )


class FeatureFilter(django_filters.FilterSet):
    """Contains the filters to use when retrieving features."""

    class Meta:
        model = models.Feature
        fields = [
            "distance_lte",
            "updated_since",
            "tagged_with_any",
            "tagged_with_all",
            "category",
        ]

    distance_lte = DistanceFilter(
        field_name="geometry",
        lookup_expr="distance_lte",
        label=_("Fetch features within a given distance from the given geometry"),
    )
    updated_since = django_filters.IsoDateTimeFilter(
        method="filter_updated_since",
        label=_("Fetch features that have changed since specified timestamp"),
    )
    tagged_with_any = StringListFilter(
        method="filter_tagged_with_any",
        label=_("Fetch features tagged with any of the specified tags (ids)"),
    )
    tagged_with_all = StringListFilter(
        method="filter_tagged_with_all",
        label=_("Fetch features tagged with all of the specified tags (ids)"),
    )
    category = StringListFilter(
        method="filter_category", label=_("Fetch features from included categories")
    )

    def filter_updated_since(self, queryset, name, value):
        return queryset.filter(
            Q(overrides__modified_at__gt=value) | Q(source_modified_at__gt=value)
        ).distinct()  # Distinct because filtering on ForeignKey relation.

    def filter_tagged_with_any(self, queryset, name, value):
        return queryset.filter(
            tags__in=value
        ).distinct()  # Distinct because filtering on ForeignKey relation.

    def filter_tagged_with_all(self, queryset, name, value):
        for v in value:
            queryset = queryset.filter(tags=v)
        return queryset

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__in=value)


class Feature(graphql_geojson.GeoJSONType):
    """Features in Ahti are structured according to GeoJSON specification.

    All Ahti specific attributes are contained within attribute `properties`.

    **Note!** `Feature.type` always has the value `Feature`.
    """

    class Meta:
        fields = (
            "id",
            "category",
            "created_at",
            "contact_info",
            "teaser",
            "details",
            "price_tag",
            "geometry",
            "images",
            "links",
            "opening_hours_periods",
            "tags",
            "translations",
        )
        filterset_class = FeatureFilter
        model = models.Feature
        geojson_field = "geometry"
        interfaces = (relay.Node,)

    ahti_id = graphene.String(
        required=True,
        description=_(
            "Human readable ID. Format examples: "
            "'ahti:feature:12C4' or 'myhelsinki:place:5678'"
        ),
    )
    source = graphene.Field(
        FeatureSource, required=True, description=_("Source of the feature")
    )
    name = graphene.String(required=True, description=_("Name of the feature"))
    one_liner = graphene.String(
        required=True, description=_("Short introductory text or a tagline")
    )
    description = graphene.String(description=_("Description of the feature"))
    details = graphene.Field(
        FeatureDetails, description=_("Detailed information a feature might have")
    )
    url = graphene.String(description=_("URL for more information about this feature"))
    modified_at = graphene.DateTime(required=True)
    parents = graphene.List(
        "features.schema.Feature",
        required=True,
        description=_("Parents of this feature"),
    )
    children = graphene.List(
        "features.schema.Feature",
        required=True,
        description=_(
            "Children of this feature (ex. stops along a route, piers of a harbor etc.)"
        ),
    )

    def resolve_priceList(self: models.Feature, info, **kwargs):
        return self.price_tags.all()

    def resolve_source(self: models.Feature, info, **kwargs):
        return {
            "system": self.source_type.system,
            "type": self.source_type.type,
            "id": self.source_id,
        }

    def resolve_name(self: models.Feature, info, **kwargs):
        name_override = self.overrides.filter(field=OverrideFieldType.NAME).first()
        if name_override:
            return name_override.value
        return self.name

    def resolve_modified_at(self: models.Feature, info, **kwargs):
        latest_override = self.overrides.order_by("-modified_at").first()
        return (
            max(self.source_modified_at, latest_override.modified_at)
            if latest_override
            else self.source_modified_at
        )

    def resolve_details(self: models.Feature, info, **kwargs):
        details = {}
        for detail in self.details.all():
            # Default dict resolver will resolve this for FeatureDetails
            details[detail.type.lower()] = detail
        return details if details else None

    def resolve_parents(self: models.Feature, info, **kwargs):
        return self.parents.all()

    def resolve_children(self: models.Feature, info, **kwargs):
        return self.children.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        return (
            queryset.filter(visibility=Visibility.VISIBLE)
            .select_related("source_type", "category", "teaser")
            .prefetch_related(
                "category__translations",
                "contact_info",
                "children",
                "details",
                "price_tags",
                "price_tags__translations",
                "images",
                "images__license",
                "images__license__translations",
                "links",
                "opening_hours_periods",
                "opening_hours_periods__opening_hours",
                "opening_hours_periods__translations",
                "parents",
                "tags",
                "tags__translations",
                "teaser__translations",
                "translations",
            )
        )


class Query(graphene.ObjectType):
    features = DjangoFilterConnectionField(
        Feature, description=_("Retrieve all features matching the given filters")
    )
    feature = graphene.Field(
        Feature,
        id=ID(description=_("The ID of the object")),
        ahti_id=String(description=_("Ahti ID of the object")),
        description=_("Retrieve a single feature"),
    )
    tags = graphene.List(Tag, description=_("Retrieve all tags"))

    def resolve_feature(self, info, id=None, ahti_id=None, **kwargs):
        if id:
            return relay.Node.get_node_from_global_id(info, id, only_type=Feature)
        if ahti_id:
            try:
                return Feature.get_queryset(models.Feature.objects, info).ahti_id(
                    ahti_id=ahti_id
                )
            except models.Feature.DoesNotExist:
                return None
        raise GraphQLError("You must provide either `id` or `ahtiId`.")

    def resolve_tags(self, info, **kwargs):
        return models.Tag.objects.all()
