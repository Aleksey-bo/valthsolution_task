import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your tests here.
@pytest.mark.django_db
class TestAuthViewSet:
    def test_sign_up(self, client):
        url = reverse("auth-sign_up")
        data = {
            "username": "test_user",
            "password": "test_password"
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert User.objects.filter(username="test_user").exists()

    def test_sign_in(self, client):
        user_instance = User.objects.create(username="test_user")
        user_instance.set_password("test_password")
        user_instance.save()
        url = reverse("auth-sign_in")
        data = {
            "username": "test_user",
            "password": "test_password"
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.django_db
class TestSecureViewSet:
    def test_security(self, client):
        url = reverse("auth-sign_up")
        data = {
            "username": "test_user",
            "password": "test_password"
        }

        response = client.post(url, data, format='json')
        token = response.data.get("access_token")

        url = reverse("profile-me")
        response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")

        assert response.status_code == 200
        assert response.data.get("username") == "test_user"
