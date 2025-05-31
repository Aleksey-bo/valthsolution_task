from rest_framework.serializers import ModelSerializer

from .models import NameAggregationModel, CountryModel, RegionModel


class RegionSerializer(ModelSerializer):
    class Meta:
        model = RegionModel
        fields = ["id", "region", "subregion"]


class CountrySerializer(ModelSerializer):
    region = RegionSerializer(source="region_id")

    class Meta:
        model = CountryModel
        fields = [
            "id",
            "common_country_name",
            "official_country_name",
            "cca2",
            "independent",
            "region",
            "capital",
            "capital_lat",
            "capital_lon",
            "flag_png",
            "flag_svg",
            "flag_alt",
            "coat_of_arms_svg",
            "coat_of_arms_png",
            "borders_with"
        ]


class NameSerializer(ModelSerializer):
    country = CountrySerializer(source="country_id")

    class Meta:
        model = NameAggregationModel
        fields = [
            "id",
            "name",
            "count",
            "last_access",
            "country",
            "probability",
        ]
