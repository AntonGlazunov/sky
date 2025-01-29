
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sky_api.models import City
from sky_api.serializers import CityCreateSerializer
from sky_api.services import get_sky, planning_mailing

a = City
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
        planning_mailing()

