from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from ..schemas import AdvisoryCreate, Feedback, Document, JobResponse
from ..security.auth import farmer, current_user, owned_advisory, uid, stamp, rate_limit, audit
from ..db import db
router = APIRouter()
@router.post('/advisories', response_model=JobResponse, status_code=202)
async def create_advisory(body: AdvisoryCreate, user=Depends(farmer)):
    await rate_limit(f'advisory:{user["id"]}', 20, 60)
    existing = await db.advisories.find_one({'owner': user['id'], 'idempotency_key': body.idempotency_key}, {'_id': 0})
    if existing:
        if existing['inputs'] != body.model_dump(): raise HTTPException(409, 'This request key was already used for different content')
        return {'job_id': existing['job_id'], 'advisory_id': existing['id'], 'status': existing['status']}
    field = await db.fields.find_one({'id': body.field_id, 'owner': user['id']}, {'_id': 0})
    if not field: raise HTTPException(404, 'Field not found')
    for identifier in body.upload_ids:
        if not await db.uploads.find_one({'id': identifier, 'owner': user['id']}, {'_id': 0}): raise HTTPException(404, 'Attachment not found')
    identifier, job_id = uid(), uid()
    doc = {'id': identifier, 'owner': user['id'], 'farmer_name': user['profile']['name'], 'field_id': field['id'], 'field_name': field['name'], 'crop': field['crop'], 'location': field['location'], 'inputs': body.model_dump(), 'idempotency_key': body.idempotency_key, 'job_id': job_id, 'status': 'processing', 'expert_access': False, 'title': body.query[:100] or f'{field["crop"]} · {body.input_type} consultation', 'created_at': stamp(), 'updated_at': stamp(), 'mode': 'demo', 'monitoring_eligible': False, 'auto_training': False}
    try: await db.advisories.insert_one(doc.copy())
    except DuplicateKeyError: return await create_advisory(body, user)
    await db.jobs.insert_one({'id': job_id, 'owner': user['id'], 'resource_id': identifier, 'operation': 'advisory', 'status': 'queued', 'retries': 0, 'provider_error': None, 'next_attempt_at': stamp(), 'created_at': stamp(), 'updated_at': stamp()})
    return {'job_id': job_id, 'advisory_id': identifier, 'status': 'queued'}
@router.get('/advisories', response_model=list[Document])
async def list_advisories(user=Depends(farmer)):
    return await db.advisories.find({'owner': user['id']}, {'_id': 0}).sort('created_at', -1).to_list(500)
@router.get('/advisories/{identifier}', response_model=Document)
async def advisory(identifier: str, user=Depends(current_user)):
    doc = await owned_advisory(identifier, user)
    doc['reviews'] = await db.expert_reviews.find({'advisory_id': identifier}, {'_id': 0}).sort('created_at', -1).to_list(100)
    return doc
@router.post('/advisories/{identifier}/feedback')
async def feedback(identifier: str, body: Feedback, user=Depends(farmer)):
    await owned_advisory(identifier, user)
    await db.advisories.update_one({'id': identifier}, {'$set': {'feedback': {**body.model_dump(), 'created_at': stamp()}}})
    await audit(user['id'], 'advisory.feedback', identifier, {'helpful': body.helpful})
    return {'status': 'saved'}
@router.post('/advisories/{identifier}/whatsapp', response_model=JobResponse, status_code=202)
async def whatsapp(identifier: str, user=Depends(farmer)):
    await owned_advisory(identifier, user)
    await rate_limit(f'whatsapp:{user["id"]}', 5, 60)
    prior = await db.jobs.find_one({'owner': user['id'], 'resource_id': identifier, 'operation': 'whatsapp', 'status': {'$in': ['queued', 'running']}}, {'_id': 0})
    if prior: return {'job_id': prior['id'], 'status': prior['status'], 'mode': 'simulated'}
    job_id = uid()
    await db.jobs.insert_one({'id': job_id, 'owner': user['id'], 'resource_id': identifier, 'operation': 'whatsapp', 'status': 'queued', 'mode': 'simulated', 'retries': 0, 'provider_error': None, 'next_attempt_at': stamp(), 'created_at': stamp(), 'updated_at': stamp()})
    return {'job_id': job_id, 'status': 'queued', 'mode': 'simulated'}
@router.get('/jobs/{identifier}', response_model=Document)
async def job(identifier: str, user=Depends(current_user)):
    doc = await db.jobs.find_one({'id': identifier, 'owner': user['id']}, {'_id': 0})
    if not doc: raise HTTPException(404, 'Job not found')
    return doc