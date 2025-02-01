from django.core.exceptions import ValidationError
from django.db import models

NULLABLE = {'blank': True, 'null': True}

class City(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', **NULLABLE)
    owner = models.ForeignKey('users_api.User', on_delete=models.CASCADE, verbose_name='Владелец', **NULLABLE)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, verbose_name='широта', default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='высота', default=0)

    def __str__(self):
        return f'{self.name} {self.latitude}, {self.longitude}'

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Temp(models.Model):
    city = models.ForeignKey('sky_api.City', on_delete=models.CASCADE, verbose_name='Город')
    date_time = models.DateTimeField(verbose_name='Дата и время', **NULLABLE)
    temp = models.SmallIntegerField(verbose_name='Температура', **NULLABLE)
    humidity = models.SmallIntegerField(verbose_name='`Влажность`', **NULLABLE)
    precipitation = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='Осадки', **NULLABLE)
    wind = models.SmallIntegerField(verbose_name='Скорость ветра', **NULLABLE)

    def __str__(self):
        return f'{self.city} {self.date_time} {self.temp} {self.humidity} {self.precipitation} {self.wind}'

    class Meta:
        verbose_name = 'Погода'
        verbose_name_plural = 'Погода'
