import asyncio
from datetime import timedelta
from ..db import db
from ..security.auth import stamp, now, audit
from ..integrations.adapters import whatsapp_adapter
from .advisory_service import process_advisory
async def worker():
    while True:
        try:
            job = await db.jobs.find_one_and_update({'status': 'queued', 'next_attempt_at': {'$lte': stamp()}}, {'$set': {'status': 'running', 'updated_at': stamp()}}, return_document=True, projection={'_id': 0})
        except Exception:
            await asyncio.sleep(2)
            continue
        if not job:
            await asyncio.sleep(0.8)
            continue
        try:
            if job['operation'] == 'advisory':
                await asyncio.wait_for(process_advisory(job['resource_id']), timeout=20)
                update = {'status': 'completed', 'provider_error': None}
            else:
                result = await whatsapp_adapter.send(job)
                update = {'status': 'queued' if result['retryable'] else 'failed', 'provider_error': result['provider_error'], 'retries': job['retries'] + 1, 'next_attempt_at': (now() + timedelta(seconds=2 ** (job['retries'] + 1))).isoformat()}
            await db.jobs.update_one({'id': job['id']}, {'$set': {**update, 'updated_at': stamp()}})
            if update['status'] in ['failed', 'completed']:
                await audit('system', f"job.{update['status']}", job['id'], {'operation': job['operation'], 'mode': 'simulated' if job['operation'] == 'whatsapp' else 'demo'})
        except asyncio.CancelledError: raise
        except Exception:
            retry = job['retries'] + 1
            await db.jobs.update_one({'id': job['id']}, {'$set': {'status': 'queued' if retry < 3 else 'failed', 'retries': retry, 'provider_error': 'PROCESSING_UNAVAILABLE', 'next_attempt_at': (now() + timedelta(seconds=2 ** retry)).isoformat(), 'updated_at': stamp()}})
            if retry >= 3 and job['operation'] == 'advisory':
                await db.advisories.update_one({'id': job['resource_id'], 'status': 'processing'}, {'$set': {'status': 'failed', 'updated_at': stamp()}})