from django.urls import path
from rest_framework.routers import DefaultRouter

from sky_api.apps import SkyApiConfig
from sky_api.views import get_temp

app_name = SkyApiConfig.name


urlpatterns = [
    path('test/', get_temp, name='temp'),
]