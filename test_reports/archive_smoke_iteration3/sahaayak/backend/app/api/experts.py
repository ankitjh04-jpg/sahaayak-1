import re
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ReviewCreate, Document
from ..security.auth import expert, owned_advisory, uid, stamp, audit
from ..db import db
from ..services.farmer_notifications import notify_review
router = APIRouter()
@router.get('/expert/cases', response_model=list[Document])
async def cases(user=Depends(expert)):
    return await db.advisories.find({'expert_access': True}, {'_id': 0}).sort('created_at', -1).to_list(500)
@router.post('/expert/cases/{identifier}/review', response_model=Document)
async def review(identifier: str, body: ReviewCreate, user=Depends(expert)):
    case = await owned_advisory(identifier, user)
    source = await db.knowledge_sources.find_one({'id': body.source_id, 'verified': True}, {'_id': 0})
    if not source: raise HTTPException(422, 'Select a verified source')
    if re.search(r'\d+(?:\.\d+)?\s*(?:ml|mg|kg|litre|liter|gram|%|मिली|ग्राम|ਕਿਲੋ)', body.recommendation, re.I):
        raise HTTPException(422, 'Dosage advice is not supported by the general source library. Remove dosage and refer to a verified local product label.')
    doc = {'id': uid(), 'advisory_id': identifier, 'expert_id': user['id'], 'expert_name': user['profile']['name'], **body.model_dump(), 'previous_recommendation': case.get('recommendation'), 'source': source, 'created_at': stamp(), 'mode': 'demo'}
    status = 'needs_information' if body.decision == 'needs_information' else 'verified'
    update = await db.advisories.update_one({'id': identifier, 'status': {'$in': ['pending_review', 'needs_information']}}, {'$set': {'status': status, 'expert_recommendation': body.recommendation, 'expert_name': user['profile']['name'], 'expert_review_id': doc['id'], 'updated_at': stamp(), 'monitoring_eligible': status == 'verified', 'auto_training': False}})
    if not update.modified_count: raise HTTPException(409, 'This case has already been reviewed. Refresh the queue.')
    await db.expert_reviews.insert_one(doc.copy())
    await notify_review(case, doc)
    await audit(user['id'], 'expert.reviewed', identifier, {'review_id': doc['id'], 'decision': body.decision, 'source_id': source['id'], 'auto_training': False})
    return doc