from rest_framework.decorators import api_view
from rest_framework.response import Response

from sky_api.services import get_sky


@api_view(['POST'])
def get_temp(request):
    """Полеучение координат и вывод метеоданных"""
    if request.method == 'POST':
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if isinstance(latitude, float) and isinstance(longitude, float):
            temp, press, wind = get_sky(latitude=latitude, longitude=longitude)
            return Response({"температура": temp, "давление": press, "скорость вертра": wind})
        return Response({"message": "Введите верные значения"})

# class LessonCreateAPIView(generics.CreateAPIView):
#     serializer_class = LessonSerializer
#     permission_classes = [IsAuthenticatedAndNoModer]
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
