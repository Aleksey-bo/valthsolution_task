from django.urls import path
from .views import NameView, PopularNamesView


urlpatterns = [
    path('names/', NameView.as_view(), name="names-handler"),
    path("popular-names/", PopularNamesView.as_view(), name="popular-names"),
]