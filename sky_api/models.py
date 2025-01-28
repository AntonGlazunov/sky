from django.db import models

NULLABLE = {'blank': True, 'null': True}

class City(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    x = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='X')
    y = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Y')

    def __str__(self):
        return f'{self.name} {self.x}, {self.y}'

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Temp(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, verbose_name='Город', **NULLABLE)
    temp = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Температура')

    def __str__(self):
        return f'{self.city} {self.temp}'

    class Meta:
        verbose_name = 'Прогноз'
        verbose_name_plural = 'Города'
