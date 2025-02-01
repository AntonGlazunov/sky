from rest_framework import serializers, status
from rest_framework.response import Response

from sky_api.models import City, Temp


class WeatherSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=8, decimal_places=6, required=True, help_text="Широта, диапазон -90...90")
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True, help_text="Высота, диапазон -180...180")

class WeatherResponseSerializer(serializers.Serializer):
    temp = serializers.IntegerField(help_text="Температура")
    press = serializers.IntegerField(help_text="Атмосферное давление")
    wind = serializers.IntegerField(help_text="Скорость ветра")


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude',]


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name',]

class ForecastSerializer(serializers.Serializer):
    city_name = serializers.CharField(max_length=200, required=True, help_text='Название города из списка отслеживания')
    time = serializers.CharField(max_length=5, required=True, help_text='Время в формате ЧЧ:ММ')
    param = serializers.ListField(child=serializers.CharField(max_length=13), min_length=1, max_length=4, help_text='Прогнозируемые параметры')

class ForecastResponseSerializer(serializers.Serializer):
    temp = serializers.IntegerField(help_text="Температура")
    humidity = serializers.IntegerField(help_text="Влажность")
    precipitation = serializers.DecimalField(max_digits=3, decimal_places=1, help_text="Осадки")
    wind = serializers.IntegerField(help_text="Скорость ветра")
