from rest_framework import serializers

from sky_api.models import City


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'x', 'y']
