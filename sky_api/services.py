import asyncio
import openmeteo_requests
import requests_cache
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from retry_requests import retry

from config import settings
from sky_api.models import Temp, City

scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)


def get_sky(latitude, longitude):
    """Подключение к open-meteo и получение данных температуры, давления и скорости ветра"""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "surface_pressure", "wind_speed_10m"]
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_surface_pressure = current.Variables(1).Value()
    current_wind_speed_10m = current.Variables(2).Value()
    return current_temperature_2m, current_surface_pressure, current_wind_speed_10m


def planning():
    """Планировщик для перезапуска задач в 00:00 и при запуске ПО"""
    if scheduler.get_job(job_id='start_async_code') is None:
        scheduler.add_job(start_async_code, 'interval', minutes=15, id='start_async_code')
    if scheduler.get_job(job_id='new_day') is None:
        scheduler.add_job(reset_forecast, 'cron', hour=0, id='new_day')


async def reset_forecast():
    await Temp.objects.all().delete()
    planning()


def start_async_code():
    """Выбор всех записанных городов и запуск асинхронного алгоритма получения прогноза"""
    cites = City.objects.all()
    if cites.exists():
        asyncio.run(add_forecast_in_db(cites))


async def add_forecast_in_db(cites):
    """Алгоритм получения прогноза"""
    tasks = []
    """Цикл создания асинхронного задания для запроса данных по API"""
    for city in cites:
        tasks.append(asyncio.create_task(get_forecast(city)))
    await asyncio.gather(*tasks)


async def get_forecast(city):
    """Подключение к open-meteo и получение данных температуры, давления и скорости ветра"""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(city.latitude),
        "longitude": float(city.longitude),
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    """Запись результатов выполнения запроса в БД"""
    for index, row in hourly_dataframe.iterrows():
        dict_data = {'city': city, 'date_time': row['date'], 'temp': row['temperature_2m'],
                     'humidity': row['relative_humidity_2m'], 'precipitation': row['precipitation'],
                     'wind': row['wind_speed_10m']}
        await Temp.objects.aupdate_or_create(city=city, date_time=row['date'], defaults=dict_data)
