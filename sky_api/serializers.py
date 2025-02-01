from rest_framework import serializers

from sky_api.models import City, Temp


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude',]


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name',]
