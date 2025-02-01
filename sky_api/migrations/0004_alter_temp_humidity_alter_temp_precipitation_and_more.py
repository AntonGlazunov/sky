# Generated by Django 5.1.5 on 2025-02-01 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sky_api', '0003_alter_city_latitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temp',
            name='humidity',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='`Влажность`'),
        ),
        migrations.AlterField(
            model_name='temp',
            name='precipitation',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True, verbose_name='Осадки'),
        ),
        migrations.AlterField(
            model_name='temp',
            name='temp',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Температура'),
        ),
        migrations.AlterField(
            model_name='temp',
            name='wind',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Скорость ветра'),
        ),
    ]
