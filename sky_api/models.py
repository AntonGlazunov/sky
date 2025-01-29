from django.db import models

NULLABLE = {'blank': True, 'null': True}

class City(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='широта', default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='высота', default=0)

    def __str__(self):
        return f'{self.name} {self.latitude}, {self.longitude}'

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Temp(models.Model):
    city = models.ForeignKey('sky_api.City', on_delete=models.CASCADE, verbose_name='Город', **NULLABLE)
    temp = models.SmallIntegerField(verbose_name='Температура', default=0)
    press = models.SmallIntegerField(verbose_name='Давление', default=0)
    wind = models.SmallIntegerField(verbose_name='Скорость ветра', default=0)

    def __str__(self):
        return f'{self.city} {self.temp} {self.press} {self.wind}'

    class Meta:
        verbose_name = 'Погода'
        verbose_name_plural = 'Погода'
