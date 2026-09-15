import math
from datetime import datetime, timedelta
from ..db import db
from ..security.auth import now, stamp
from ..integrations.weather import fetch_weather, weather_provider
from ..config import WEATHER_CACHE_SECONDS

def no_weather(reason, location=''):
    return {'status': 'no_data', 'location': location, 'temperature': None, 'precipitation': None, 'wind_speed': None, 'humidity': None, 'observed_at': None, 'stale': False, 'reason': reason, 'provider': weather_provider()}

async def current_weather(lat, lon, location=''):
    if lat is None or lon is None: return no_weather('Choose a mapped field or share your location to see weather.', location)
    key = f'{weather_provider()}:{lat:.3f}:{lon:.3f}'
    cached = await db.weather_cache.find_one({'key': key}, {'_id': 0})
    if cached and (now() - datetime.fromisoformat(cached['fetched_at'])).total_seconds() < WEATHER_CACHE_SECONDS:
        data = cached['data']
        age = (now() - datetime.fromisoformat(data['observed_at'])).total_seconds()
        if -3600 <= age < 7200:
            return {**data, 'status': 'cached', 'stale': False, 'location': location, 'fetched_at': cached['fetched_at']}
    try:
        data = await fetch_weather(round(lat, 3), round(lon, 3))
        if not isinstance(data['temperature'], (int, float)) or not math.isfinite(data['temperature']):
            raise ValueError('INVALID_WEATHER')
        age = (now() - datetime.fromisoformat(data['observed_at'])).total_seconds()
        if age < -3600 or age > 7200: raise ValueError('STALE_WEATHER')
        data.update({'latitude': round(lat, 3), 'longitude': round(lon, 3)})
        fetched_at = stamp()
        await db.weather_cache.update_one({'key': key}, {'$set': {'key': key, 'data': data, 'fetched_at': fetched_at, 'expires_at': now() + timedelta(hours=24)}}, upsert=True)
        return {**data, 'status': 'live', 'stale': False, 'location': location, 'fetched_at': fetched_at}
    except Exception:
        # No raw provider exception is logged or returned (may contain API key URLs).
        if cached and (now() - datetime.fromisoformat(cached['data']['observed_at'])).total_seconds() <= 86400:
            return {**cached['data'], 'status': 'stale', 'stale': True, 'location': location, 'fetched_at': cached['fetched_at'], 'reason': 'Live weather is unavailable. Showing an older estimate; do not use it for treatment decisions.'}
        return no_weather('Weather is temporarily unavailable. Please try again later.', location)