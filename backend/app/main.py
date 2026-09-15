import asyncio
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import db, client, create_indexes
from .config import DEMO_MODE, CORS_ORIGINS
from .api import auth, fields, advisories, experts, uploads, health, notifications, predict
from .services.farmer_notifications import repair_notifications
from .seed import seed
from .services.notification_service import worker
from .ml import pipeline
from .security.auth import stamp
async def _warm_model():
    try: await asyncio.to_thread(pipeline.warmup)
    except Exception: pass
@asynccontextmanager
async def lifespan(app):
    await db.command('ping')
    await create_indexes()
    if DEMO_MODE: await seed()
    await repair_notifications()
    await db.jobs.update_many({'status': 'running'}, {'$set': {'status': 'queued', 'next_attempt_at': stamp()}})
    async for case in db.advisories.find({'status': 'processing'}, {'_id': 0}):
        await db.jobs.update_one({'id': case['job_id']}, {'$setOnInsert': {'id': case['job_id'], 'owner': case['owner'], 'resource_id': case['id'], 'operation': 'advisory', 'status': 'queued', 'retries': 0, 'provider_error': None, 'next_attempt_at': stamp(), 'created_at': stamp(), 'updated_at': stamp()}}, upsert=True)
    task = asyncio.create_task(worker())
    asyncio.create_task(_warm_model())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError): await task
    client.close()
app = FastAPI(title='Sahaayak API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False, allow_methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Authorization', 'Content-Type'])
for module in [
    auth,
    fields,
    advisories,
    experts,
    uploads,
    health,
    notifications,
    predict,
]:
    app.include_router(module.router, prefix="/api/v1")