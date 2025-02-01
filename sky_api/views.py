
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sky_api.models import City, Temp
from sky_api.serializers import CityCreateSerializer, CityListSerializer
from sky_api.services import get_sky, get_datetime, start_async_code


@api_view(['POST'])
def get_weather(request):
    """Полеучение координат и вывод метеоданных"""
    if request.method == 'POST':
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if isinstance(latitude, float) and isinstance(longitude, float):
            temp, press, wind = get_sky(latitude=latitude, longitude=longitude)
            return Response({"температура": temp, "давление": press, "скорость вертра": wind})
        return Response({"message": "Введите верные значения"})


class CityCreateAPIView(generics.CreateAPIView):
    serializer_class = CityCreateSerializer

    def perform_create(self, serializer):
        serializer.save()
        start_async_code()


class CityListAPIView(generics.ListAPIView):
    serializer_class = CityListSerializer
    queryset = City.objects.all()


@api_view(['POST'])
def get_forecast(request):
    """Полеучение координат и вывод метеоданных"""
    if request.method == 'POST':
        city_name = request.data.get('city_name')
        params = request.data.get('param')
        city = City.objects.filter(name=city_name)
        time_user = request.data.get('time')
        param_dict = {}
        try:
            date_time = get_datetime(time_user)
            if city.exists():
                temp_object = Temp.objects.filter(city=city[0], date_time=date_time)
                if isinstance(params, list):
                    for param in params:
                        if param == 'temp':
                            param_dict['Температура'] = temp_object[0].temp
                        elif param == 'humidity':
                            param_dict['Влажность'] = temp_object[0].humidity
                        elif param == 'precipitation':
                            param_dict['Осадки'] = temp_object[0].precipitation
                        elif param == 'wind':
                            param_dict['Скорость ветра'] = temp_object[0].wind
                        else:
                            return Response({
                                "message": f"Неверный параметр {param}, выберете параметры из списка: temp, humidity, precipitation, wind"})
                else:
                    return Response({"message": "Пареметры нужно передать в виде списка"})
            else:
                return Response({"message": "Неверное название города"})
            return Response(param_dict)
        except ValueError:
            return Response({"message": "Неверные данные в поле time, введите в формате ЧЧ:ММ"})
