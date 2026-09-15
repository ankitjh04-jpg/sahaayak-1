import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / '.env')
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
DEMO_MODE = os.environ['DEMO_MODE'].lower() == 'true'
DEMO_OTP = os.environ['DEMO_OTP']
FARMER_PHONE = os.environ['DEMO_FARMER_PHONE']
EXPERT_PHONE = os.environ['DEMO_EXPERT_PHONE']
DEMO_EXPERT_EMAIL = os.environ.get('DEMO_EXPERT_EMAIL', 'ankitjh04@gmail.com').strip().lower()
DEMO_EXPERT_PASSWORD = os.environ.get('DEMO_EXPERT_PASSWORD', 'SahaayakExpert2026!')
DEMO_EXPERT_NAME = os.environ.get('DEMO_EXPERT_NAME', 'Ankit')
CORS_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ORIGINS', os.environ['FRONTEND_ORIGIN']).split(',') if origin.strip()]
DEMO_EXPERT_ACCOUNTS = [
	(DEMO_EXPERT_EMAIL, DEMO_EXPERT_PASSWORD, DEMO_EXPERT_NAME),
	('gulshankumar2542004@gmail.com', 'Kumar@123', 'Gulshan Kumar'),
	('expert.one@sahaayak.demo', 'ExpertOne@2026', 'Expert One'),
	('expert.two@sahaayak.demo', 'ExpertTwo@2026', 'Expert Two'),
	('agri.specialist@sahaayak.demo', 'AgriSpecialist@2026', 'Agri Specialist'),
]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
_storage = Path(os.environ['STORAGE_ROOT'])
STORAGE_ROOT = (_storage if _storage.is_absolute() else BACKEND_ROOT / _storage).resolve()
FRONTEND_ORIGIN = os.environ['FRONTEND_ORIGIN']
MAX_UPLOAD_BYTES = int(os.environ['MAX_UPLOAD_BYTES'])
OSM_TILE_URL = os.environ['OSM_TILE_URL']
OTP_PROVIDER = os.environ.get('OTP_PROVIDER', 'auto').lower()
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')
TWILIO_VERIFY_BASE_URL = os.environ['TWILIO_VERIFY_BASE_URL']
WEATHER_PROVIDER = os.environ.get('WEATHER_PROVIDER', 'auto').lower()
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
OPENWEATHER_URL = os.environ['OPENWEATHER_URL']
OPEN_METEO_URL = os.environ['OPEN_METEO_URL']
GOOGLE_MAPS_BROWSER_KEY = os.environ.get('GOOGLE_MAPS_BROWSER_KEY', '')
GOOGLE_MAPS_MAP_ID = os.environ.get('GOOGLE_MAPS_MAP_ID', '')
WEATHER_CACHE_SECONDS = int(os.environ.get('WEATHER_CACHE_SECONDS', '600'))