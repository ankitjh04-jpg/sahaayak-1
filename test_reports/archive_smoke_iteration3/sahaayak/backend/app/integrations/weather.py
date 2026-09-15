from datetime import datetime, timezone
import httpx
from .. import config

def weather_provider():
    if config.WEATHER_PROVIDER == 'auto':
        return 'openweather' if config.OPENWEATHER_API_KEY else 'open-meteo'
    return config.WEATHER_PROVIDER

def condition(code):
    if code == 0: return 'Clear sky'
    if code in (1, 2): return 'Partly cloudy'
    if code == 3: return 'Overcast'
    if code in (45, 48): return 'Fog'
    if code in (51, 53, 55, 56, 57): return 'Drizzle'
    if code in (61, 63, 65, 66, 67, 80, 81, 82): return 'Rain'
    if code in (71, 73, 75, 77, 85, 86): return 'Snow'
    if code in (95, 96, 99): return 'Thunderstorm'
    return 'Conditions unavailable'

class OpenMeteoAdapter:
    async def get(self, lat, lon):
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(config.OPEN_METEO_URL, params={'latitude': lat, 'longitude': lon, 'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m', 'temperature_unit': 'celsius', 'wind_speed_unit': 'kmh', 'precipitation_unit': 'mm', 'timeformat': 'unixtime', 'timezone': 'UTC', 'forecast_days': 1})
            response.raise_for_status()
        current = response.json()['current']
        return {'provider': 'Open-Meteo', 'temperature': current['temperature_2m'], 'humidity': current.get('relative_humidity_2m'), 'precipitation': current.get('precipitation'), 'precipitation_interval_seconds': current['interval'], 'wind_speed': current.get('wind_speed_10m'), 'condition': condition(current.get('weather_code')), 'observed_at': datetime.fromtimestamp(current['time'], timezone.utc).isoformat(), 'source_kind': 'weather model estimate', 'attribution': 'Open-Meteo · CC BY 4.0'}

class OpenWeatherAdapter:
    async def get(self, lat, lon):
        if not config.OPENWEATHER_API_KEY: raise ValueError('WEATHER_NOT_CONFIGURED')
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(config.OPENWEATHER_URL, params={'lat': lat, 'lon': lon, 'appid': config.OPENWEATHER_API_KEY, 'units': 'metric'})
            response.raise_for_status()
        data = response.json()
        wind = data.get('wind', {}).get('speed')
        return {'provider': 'OpenWeather', 'temperature': data['main']['temp'], 'humidity': data['main'].get('humidity'), 'precipitation': data.get('rain', {}).get('1h'), 'precipitation_interval_seconds': 3600, 'wind_speed': round(wind * 3.6, 1) if wind is not None else None, 'condition': data.get('weather', [{}])[0].get('description', 'Conditions unavailable'), 'observed_at': datetime.fromtimestamp(data['dt'], timezone.utc).isoformat(), 'source_kind': 'provider current conditions', 'attribution': 'OpenWeather'}

async def fetch_weather(lat, lon):
    provider = weather_provider()
    if provider == 'open-meteo': return await OpenMeteoAdapter().get(lat, lon)
    if provider == 'openweather': return await OpenWeatherAdapter().get(lat, lon)
    raise ValueError('WEATHER_NOT_CONFIGURED')