from .weather_service import current_weather
async def assess(field, inputs):
    weather = await current_weather(field.get('latitude'), field.get('longitude'), field['location'])
    missing = ['Expert-confirmed diagnosis']
    if weather['status'] not in ('live', 'cached') or weather.get('stale'): missing.append('Current weather data')
    if field.get('soil_profile', {}).get('ph') is None: missing.append('Soil test values')
    if not inputs.get('query'): missing.append('Typed description of symptoms')
    return {'level': 'unknown', 'score': None, 'method': 'data-completeness rules', 'weather': weather, 'missing_inputs': missing, 'reason': 'Insufficient verified inputs for a field-specific risk estimate.'}