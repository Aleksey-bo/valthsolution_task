from datetime import timedelta, datetime
from unittest.mock import patch, Mock

import pytest
from django.urls import reverse
from django.utils import timezone

from .models import CountryModel
from .views import NameView

# Create your tests here.
@pytest.mark.django_db
class TestNameView:
    def test_name_view(self, client):
        name = "Alex"
        url = reverse("names-handler")
        response = client.get(f"{url}?name={name}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        for obj in data:
            last_access_str = obj.get("last_access")
            last_access_dt = datetime.fromisoformat(last_access_str.replace("Z", "+00:00"))

            assert "name" in obj and obj.get("name") is not None
            assert obj.get("name") == name.lower()
            assert "last_access" in obj
            assert timezone.now() - last_access_dt < timedelta(days=1)
            assert "country" in obj and obj.get("country")

    def test_fetch_data(self):
        with patch('aggregation.views.requests.get') as mock_get:
            name_response = Mock()
            name_response.json.return_value = {
                "name": "alex",
                "country": [
                    {"country_id": "US", "probability": 0.5},
                    {"country_id": "GB", "probability": 0.3}
                ]
            }

            country_response = Mock()
            country_response.json.return_value = [
                {
                    "cca2": "US",
                    "name": {"common": "United States", "official": "United States of America"},
                    "independent": True,
                    "region": "Americas",
                    "subregion": "Northern America",
                    "capital": ["Washington D.C."],
                    "capitalInfo": {"latlng": [38.9, -77.04]},
                    "flags": {"png": "url_png_us", "svg": "url_svg_us", "alt": "flag alt us"},
                    "coatOfArms": {"png": "coa_png_us", "svg": "coa_svg_us"},
                    "borders": ["CAN", "MEX"]
                },
                {
                    "cca2": "GB",
                    "name": {"common": "United Kingdom", "official": "United Kingdom of Great Britain and Northern Ireland"},
                    "independent": True,
                    "region": "Europe",
                    "subregion": "Northern Europe",
                    "capital": ["London"],
                    "capitalInfo": {"latlng": [51.5, -0.12]},
                    "flags": {"png": "url_png_gb", "svg": "url_svg_gb", "alt": "flag alt gb"},
                    "coatOfArms": {"png": "coa_png_gb", "svg": "coa_svg_gb"},
                    "borders": ["IRL"]
                }
            ]

            mock_get.side_effect = [name_response, country_response]

            view = NameView()
            result = view._fetch_data("alex")

            assert isinstance(result, list)
            assert len(result) == 2
            assert CountryModel.objects.filter(cca2="US").exists()
            assert CountryModel.objects.filter(cca2="GB").exists()


@pytest.mark.django_db
class TestPopularNameView:
    def test_popular_name(self, client):
        url = reverse("names-handler")
        response = client.get(f"{url}?name=Alex")

        country = "CZ"
        url = reverse("popular-names")
        response = client.get(f"{url}?country={country}")
        print(response.json())

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for obj in data:
            assert "country" in obj
            assert obj.get("country").get("cca2") == country




