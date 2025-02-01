from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sky_api.models import City, Temp
from sky_api.serializers import CityCreateSerializer, CityListSerializer, WeatherSerializer, WeatherResponseSerializer, \
    ForecastSerializer, ForecastResponseSerializer
from sky_api.services import get_sky, get_datetime, start_async_code
from users_api.permissions import IsOwner


@extend_schema(
    summary="Получение текущей погоды по координатам",
    request=WeatherSerializer,
    responses={
        201: WeatherResponseSerializer,
        400: {"message": "Введите верные значения"},
    }
)
@api_view(['POST'])
def get_weather(request):
    """Получение координат и вывод метеоданных"""
    if request.method == 'POST':
        if isinstance(request.data.get('latitude'), int) and isinstance(request.data.get('longitude'), int):
            latitude = float(request.data.get('latitude'))
            longitude = float(request.data.get('longitude'))
        else:
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
        if isinstance(latitude, float) and isinstance(longitude, float):
            if 90 >= latitude >= -90 and 180 >= longitude >= -180:
                temp, press, wind = get_sky(latitude=latitude, longitude=longitude)
                return Response({"температура": temp, "давление": press, "скорость ветра": wind},
                                status=status.HTTP_200_OK)
        return Response({"message": "Введите верные значения"}, status=status.HTTP_400_BAD_REQUEST)


class CityCreateAPIView(generics.CreateAPIView):
    serializer_class = CityCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not 90.0 >= float(serializer.validated_data['latitude']) >= -90.0:
            raise serializers.ValidationError({'latitude': "значение должно быть в диапазоне -90 - 90"})
        if not 180.0 >= float(serializer.validated_data['longitude']) >= -180.0:
            raise serializers.ValidationError({'longitude': 'значение должно быть в диапазоне -180 - 180'})
        if City.objects.filter(owner=self.request.user, name=serializer.validated_data['name']).exists():
            raise serializers.ValidationError({"message": "Такой город уже добавлен в список отслеживания"})
        else:
            serializer.save(owner=self.request.user)
            start_async_code()


class CityListAPIView(generics.ListAPIView):
    serializer_class = CityListSerializer
    queryset = City.objects.all()
    permission_classes = [IsOwner]

    def get_queryset(self):
        lesson = City.objects.filter(owner=self.request.user)
        return lesson


@extend_schema(
    summary="Получение прогноза на заданное время в заданном городе",
    request=ForecastSerializer,
    responses={
        201: ForecastResponseSerializer,
        400: {},
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_forecast(request):
    """Полеучение координат и вывод метеоданных"""
    if request.method == 'POST':
        user = request.user
        city_name = request.data.get('city_name')
        params = request.data.get('param')
        city = City.objects.filter(owner=user, name=city_name)
        time_user = request.data.get('time')
        param_dict = {}
        try:
            date_time = get_datetime(time_user)
            if city.exists():
                temp_object = Temp.objects.filter(city=city[0], date_time=date_time)
                if isinstance(params, list):
                    for param in params:
                        if param == 'temp':
                            param_dict['temp'] = temp_object[0].temp
                        elif param == 'humidity':
                            param_dict['humidity'] = temp_object[0].humidity
                        elif param == 'precipitation':
                            param_dict['precipitation'] = temp_object[0].precipitation
                        elif param == 'wind':
                            param_dict['wind'] = temp_object[0].wind
                        else:
                            return Response({
                                "message": f"Неверный параметр {param}, выберете параметры из списка: temp, humidity, precipitation, wind"},
                                status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Пареметры нужно передать в виде списка"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Неверное название города"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(param_dict, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"message": "Неверные данные в поле time, введите в формате ЧЧ:ММ"},
                            status=status.HTTP_400_BAD_REQUEST)
