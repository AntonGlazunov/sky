import asyncio
import datetime

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
        "minutely_15": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    minutely_15 = response.Minutely15()
    minutely_15_temperature_2m = minutely_15.Variables(0).ValuesAsNumpy()
    minutely_15_relative_humidity_2m = minutely_15.Variables(1).ValuesAsNumpy()
    minutely_15_precipitation = minutely_15.Variables(2).ValuesAsNumpy()
    minutely_15_wind_speed_10m = minutely_15.Variables(3).ValuesAsNumpy()

    minutely_15_data = {"date": pd.date_range(
        start=pd.to_datetime(minutely_15.Time(), unit="s", utc=True),
        end=pd.to_datetime(minutely_15.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=minutely_15.Interval()),
        inclusive="left"
    )}
    minutely_15_data["temperature_2m"] = minutely_15_temperature_2m
    minutely_15_data["relative_humidity_2m"] = minutely_15_relative_humidity_2m
    minutely_15_data["precipitation"] = minutely_15_precipitation
    minutely_15_data["wind_speed_10m"] = minutely_15_wind_speed_10m
    minutely_15_dataframe = pd.DataFrame(data=minutely_15_data)
    """Запись результатов выполнения запроса в БД"""
    for index, row in minutely_15_dataframe.iterrows():
        dict_data = {'city': city, 'date_time': row['date'], 'temp': row['temperature_2m'],
                     'humidity': row['relative_humidity_2m'], 'precipitation': row['precipitation'],
                     'wind': row['wind_speed_10m']}
        await Temp.objects.aupdate_or_create(city=city, date_time=row['date'], defaults=dict_data)


def get_datetime(time):
    offset = datetime.timedelta(hours=0)
    tz = datetime.timezone(offset, name='O')
    time_user = datetime.datetime.strptime(time, "%H:%M")
    datetime_now = datetime.datetime.now(tz=tz)
    minutes = time_user.minute
    rounded_minutes = (minutes + 7) // 15 * 15
    if rounded_minutes >= 60:
        rounded_minutes = 0
        time_user += datetime.timedelta(hours=1)
    rounded_time = time_user.replace(day=datetime_now.day, month=datetime_now.month, year=datetime_now.year,
                                     minute=rounded_minutes, second=0, microsecond=0, tzinfo=tz)
    return rounded_time
