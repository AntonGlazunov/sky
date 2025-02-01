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


