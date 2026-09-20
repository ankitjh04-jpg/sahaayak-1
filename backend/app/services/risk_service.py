from .weather_service import current_weather
from .copy import missing_labels, pick
async def assess(field, inputs, language='en'):
    weather = await current_weather(field.get('latitude'), field.get('longitude'), field['location'])
    labels = missing_labels(language)
    missing = [labels['diagnosis']]
    if weather['status'] not in ('live', 'cached') or weather.get('stale'): missing.append(labels['weather'])
    if field.get('soil_profile', {}).get('ph') is None: missing.append(labels['soil'])
    if not inputs.get('query'): missing.append(labels['description'])
    return {'level': 'unknown', 'score': None, 'method': 'data-completeness rules', 'weather': weather, 'missing_inputs': missing, 'reason': pick(language, 'risk_reason')}