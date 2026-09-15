from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URL, DB_NAME
client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

async def create_indexes():
    for collection in ['users', 'fields', 'advisories', 'expert_reviews', 'uploads', 'knowledge_sources', 'jobs', 'audit_logs', 'notifications']:
        await db[collection].create_index('id', unique=True)
    indexes = await db.users.index_information()
    if 'phone_1' in indexes and not indexes['phone_1'].get('sparse'):
        await db.users.drop_index('phone_1')
    await db.users.create_index('phone', unique=True, sparse=True)
    await db.users.create_index('email', unique=True, sparse=True)
    await db.notifications.create_index([('owner', 1), ('created_at', -1)])
    await db.weather_cache.create_index('key', unique=True)
    await db.weather_cache.create_index('expires_at', expireAfterSeconds=0)
    await db.sessions.create_index('token_hash', unique=True)
    await db.sessions.create_index('expires_at', expireAfterSeconds=0)
    await db.otps.create_index('phone', unique=True)
    await db.otps.create_index('expires_at', expireAfterSeconds=0)
    await db.rate_limits.create_index('expires_at', expireAfterSeconds=0)
    await db.fields.create_index([('owner', 1), ('created_at', -1)])
    await db.advisories.create_index([('owner', 1), ('idempotency_key', 1)], unique=True)
    await db.advisories.create_index([('status', 1), ('created_at', -1)])
    await db.uploads.create_index([('owner', 1), ('checksum', 1)], unique=True)
    await db.jobs.create_index([('status', 1), ('next_attempt_at', 1)])
    await db.expert_reviews.create_index([('advisory_id', 1), ('created_at', -1)])