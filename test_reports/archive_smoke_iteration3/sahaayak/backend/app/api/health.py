from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import db
from ..schemas import HealthResponse, Document
from ..security.auth import current_user, rate_limit
from ..integrations.otp import otp_mode
from ..integrations.weather import weather_provider
from ..services.weather_service import current_weather
from ..config import DEMO_MODE, OSM_TILE_URL, GOOGLE_MAPS_BROWSER_KEY, GOOGLE_MAPS_MAP_ID
router = APIRouter()

@router.get('/health', response_model=HealthResponse)
async def health():
    try: await db.command('ping')
    except Exception: raise HTTPException(503, 'Database unavailable')
    return {'status': 'ok', 'database': 'connected', 'mode': 'demo' if DEMO_MODE else 'configured', 'adapters': {'otp': otp_mode(), 'expert_auth': 'password', 'vision': 'no_data', 'voice': 'unavailable', 'weather': weather_provider(), 'maps': 'google' if GOOGLE_MAPS_BROWSER_KEY else 'openstreetmap', 'whatsapp': 'simulated', 'storage': 'private_local'}}

@router.get('/knowledge-sources', response_model=list[Document])
async def sources(user=Depends(current_user)): return await db.knowledge_sources.find({'verified': True}, {'_id': 0}).to_list(100)

@router.get('/weather')
async def weather(latitude: float | None = Query(None, ge=-90, le=90), longitude: float | None = Query(None, ge=-180, le=180), field_id: str | None = None, user=Depends(current_user)):
    await rate_limit(f'weather:{user["id"]}', 30, 60)
    if (latitude is None) != (longitude is None): raise HTTPException(422, 'Provide both latitude and longitude')
    location = 'Your shared location' if latitude is not None else ''
    if field_id:
        field = await db.fields.find_one({'id': field_id, 'owner': user['id']}, {'_id': 0})
        if not field: raise HTTPException(404, 'Field not found')
        latitude, longitude, location = field.get('latitude'), field.get('longitude'), field['location']
    elif latitude is None:
        field = await db.fields.find_one({'owner': user['id'], 'latitude': {'$ne': None}, 'longitude': {'$ne': None}}, {'_id': 0})
        if field: latitude, longitude, location = field['latitude'], field['longitude'], field['location']
    return await current_weather(latitude, longitude, location)

@router.get('/config')
async def public_config():
    # Google browser keys are public identifiers; restrict by API + HTTP referrer.
    return {'demo_mode': DEMO_MODE, 'map_tile_url': OSM_TILE_URL, 'languages': ['en', 'hi', 'pa'], 'otp_mode': otp_mode(), 'weather_provider': weather_provider(), 'google_maps_browser_key': GOOGLE_MAPS_BROWSER_KEY, 'google_maps_map_id': GOOGLE_MAPS_MAP_ID, 'expert_auth': 'email_password', 'aadhaar_mode': 'demo_only'}