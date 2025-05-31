from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests

from .models import NameAggregationModel, CountryModel, RegionModel
from .serializer import NameSerializer


# Create your views here.
class NameView(APIView):

    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "name",
                    openapi.IN_QUERY,
                    description="Name for search",
                    type=openapi.TYPE_STRING,
                    required=True
                )
            ],
            responses={
                200: NameSerializer(),
                400: openapi.Response(description="Name parameter is required"),
                500: openapi.Response(description="Internal Server Error")
            }
    )
    def get(self, request):
        try:
            name = request.query_params.get("name")
            if not name:
                return Response({"error": "Name parameter is required"}, status=400)

            name = name.lower()
            instances = NameAggregationModel.objects.filter(
                    name=name,
                    last_access__gte=timezone.now() - timedelta(days=1)
                )

            if not instances.exists():
                instances = self._fetch_data(name=name)
            else:
                for instance in instances:
                    instance.count += 1
                    instance.last_access = timezone.now()
                    instance.save()

            serializer = NameSerializer(instances, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=500)

    def _fetch_data(self, name: str):
        try:
            res = []
            name_obj = requests.get(f"https://api.nationalize.io/?name={name}").json()
            if not name_obj:
                return []

            countries = name_obj.get("country", [])
            country_codes = [c["country_id"] for c in countries]
            existing_countries = {
                c.cca2: c for c in CountryModel.objects.filter(cca2__in=country_codes)
            }

            missing_codes = set(country_codes) - set(existing_countries.keys())
            country_data_map = {}

            if missing_codes:
                rest_resp = requests.get(
                    f"https://restcountries.com/v3.1/alpha?codes={','.join(missing_codes)}"
                ).json()

                for data in rest_resp:
                    cca2 = data.get("cca2")
                    if cca2:
                        country_data_map[cca2] = data

            for cca2, data in country_data_map.items():
                region_obj, _ = RegionModel.objects.get_or_create(
                    region=data.get("region"),
                    defaults={"subregion": data.get("subregion")}
                )
                existing_countries[cca2] = CountryModel.objects.create(
                    common_country_name=data["name"]["common"],
                    official_country_name=data["name"]["official"],
                    cca2=data["cca2"],
                    independent=data.get("independent", False),
                    region_id=region_obj,
                    capital=", ".join(data.get("capital") or []),
                    capital_lat=(data.get("capitalInfo", {}).get("latlng") or [None])[0],
                    capital_lon=(data.get("capitalInfo", {}).get("latlng") or [None, None])[1],
                    flag_png=data.get("flags", {}).get("png"),
                    flag_svg=data.get("flags", {}).get("svg"),
                    flag_alt=data.get("flags", {}).get("alt"),
                    coat_of_arms_svg=data.get("coatOfArms", {}).get("svg"),
                    coat_of_arms_png=data.get("coatOfArms", {}).get("png"),
                    borders_with=", ".join(data.get("borders") or []),
                )

            for country in countries:
                cca2 = country["country_id"]
                instance, _ = NameAggregationModel.objects.update_or_create(
                    name=name_obj.get("name"),
                    country_id=existing_countries.get(cca2),
                    defaults={
                        "count": 1,
                        "last_access": timezone.now(),
                        "probability": country.get("probability"),
                    }
                )
                res.append(instance)

            return res
        except Exception as e:
            raise e


class PopularNamesView(APIView):

    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "country",
                    openapi.IN_QUERY,
                    description="Raiting names in country",
                    type=openapi.TYPE_STRING,
                    required=True
                )
            ],
            responses={
                200: NameSerializer(),
                400: openapi.Response(description="Country parameter is required"),
                404: openapi.Response(description="Country not found | No names found for this country"),
                500: openapi.Response(description="Internal Server Error")
            }
    )
    def get(self, request):
        try:
            country_code = request.query_params.get("country")

            if not country_code:
                return Response({"error": "Country parameter is required"}, status=400)

            instance = CountryModel.objects.filter(
                cca2=country_code.upper()
            ).first()
            if not instance:
                return Response({"error": "Country not found."}, status=404)

            top_names = (
                NameAggregationModel.objects
                .filter(country_id=instance.id)
                .order_by("-probability")[:5]
            )

            if not top_names.exists():
                return Response(
                    {"error": "No names found for this country."}, status=404
                )

            serializer = NameSerializer(top_names, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"Internal Server Error: {e}"}, status=500)