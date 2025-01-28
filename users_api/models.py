from django.contrib.auth.models import AbstractUser
from django.db import models

import sky_api.models
from sky_api.models import NULLABLE


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, verbose_name='имя пользователя')

    def __str__(self):
        return f'{self.username}, {self.pk}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class StrCity(models.Model):
    city = models.ForeignKey('sky_api.City', on_delete=models.CASCADE, verbose_name='Город',
                              related_name='city', **NULLABLE)
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Пользователь',
                              related_name='user', **NULLABLE)

    def __str__(self):
        return f'{self.city}, {self.user}'

    class Meta:
        verbose_name = 'Список городов'
        verbose_name_plural = 'Списки городов'
