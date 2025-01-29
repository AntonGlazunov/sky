import asyncio
import openmeteo_requests
import requests_cache
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


def planning_mailing():
    """Запуск планировщика задач в случае отсутствия задачи"""
    if len(scheduler.get_jobs()) == 0:
        scheduler.add_job(start_async_code, 'interval', minutes=15)
        scheduler.start()

def start_async_code():
    """Выбор всех записанных городов и запуск асинхронного алгоритма получения прогноза"""
    cites = City.objects.all()
    asyncio.run(add_forecast_in_db(cites))

async def add_forecast_in_db(cites):
    """Алгоритм получения прогноза"""
    tasks = []
    """Цикл создания асинхронного задания для запроса данных по API"""
    for city in cites:
        tasks.append(asyncio.create_task(get_forecast(city)))
    forecasts = await asyncio.gather(*tasks)
    """Запись результатов выполнения задания в БД"""
    for forecast in forecasts:
        await Temp.objects.acreate(**forecast)


async def get_forecast(city):
    """Подключение к open-meteo и получение данных температуры, давления и скорости ветра"""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "current": ["temperature_2m", "surface_pressure", "wind_speed_10m"]
    }
    """Запрос к open-meteo по API"""
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    """Запись ответа в словарь"""
    data = {'city': city, 'temp': current.Variables(0).Value(), 'press': current.Variables(1).Value(),
            'wind': current.Variables(2).Value()}
    return data

