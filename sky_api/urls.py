from django.urls import path
from sky_api.apps import SkyApiConfig
from sky_api.views import get_weather, CityCreateAPIView

app_name = SkyApiConfig.name


urlpatterns = [
    path('weather_now/', get_weather, name='weather_now'),
    path('add_city/', CityCreateAPIView.as_view(), name='add_city')
]