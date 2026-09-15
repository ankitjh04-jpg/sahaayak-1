from datetime import timedelta, date
from .db import db
from .api.auth import get_or_create
from .config import FARMER_PHONE, EXPERT_PHONE
from .security.auth import stamp, now
from .services.rag_service import SOURCE
from .services.advisory_service import process_advisory
async def seed():
    await db.knowledge_sources.update_one({'id': SOURCE['id']}, {'$set': SOURCE}, upsert=True)
    farmer = await get_or_create(FARMER_PHONE)
    expert = await db.users.find_one({'phone': EXPERT_PHONE}, {'_id': 0})
    if not expert:
        expert = {'id': 'demo-expert-historical', 'phone': EXPERT_PHONE, 'role': 'expert', 'language': 'en', 'profile': {'name': 'Dr. Meera Sharma', 'location': 'Ludhiana, Punjab'}, 'created_at': stamp(), 'updated_at': stamp()}
        await db.users.insert_one(expert.copy())
    for identifier, name, crop, acres, lat, lng in [('demo-field-wheat', 'The north field', 'Wheat', 4.5, 30.914, 75.801), ('demo-field-mustard', 'Canal-side field', 'Mustard', 2.0, 30.908, 75.815)]:
        await db.fields.update_one({'id': identifier}, {'$setOnInsert': {'id': identifier, 'owner': farmer['id'], 'name': name, 'crop': crop, 'acreage': acres, 'location': 'Ludhiana, Punjab', 'sowing_date': (date.today() - timedelta(days=65)).isoformat(), 'soil_profile': {'ph': 7.2} if crop == 'Wheat' else {}, 'latitude': lat, 'longitude': lng, 'created_at': stamp(), 'updated_at': stamp(), 'seeded': True}}, upsert=True)
    for i, title in enumerate(['Yellowing leaves in my wheat field', 'How can I monitor my mustard crop?', 'Preparing for a healthier wheat crop']):
        identifier = f'demo-advisory-{i + 1}'
        if await db.advisories.find_one({'id': identifier}, {'_id': 0}): continue
        field = 'demo-field-mustard' if i == 1 else 'demo-field-wheat'
        doc = {'id': identifier, 'owner': farmer['id'], 'farmer_name': farmer['profile']['name'], 'field_id': field, 'field_name': 'Canal-side field' if i == 1 else 'The north field', 'crop': 'Mustard' if i == 1 else 'Wheat', 'location': 'Ludhiana, Punjab', 'inputs': {'query': title, 'input_type': 'text', 'upload_ids': [], 'language': 'en'}, 'idempotency_key': identifier, 'job_id': f'seed-job-{i}', 'status': 'processing', 'title': title, 'created_at': (now() - timedelta(days=i + 1)).isoformat(), 'updated_at': stamp(), 'seeded': True, 'mode': 'demo'}
        await db.advisories.insert_one(doc.copy())
        await process_advisory(identifier)
        if i == 1:
            recommendation = 'Keep an observation record and photographs of affected and healthy plants. Prefer preventive and ecological pest management. A field diagnosis is still needed before selecting any treatment.'
            review = {'id': 'demo-review-1', 'advisory_id': identifier, 'expert_id': expert['id'], 'expert_name': expert['profile']['name'], 'decision': 'validated', 'recommendation': recommendation, 'rationale': 'Demo validation: general IPM principles are supported by the cited FAO source; no field diagnosis is confirmed.', 'source_id': SOURCE['id'], 'source': SOURCE, 'created_at': stamp(), 'mode': 'demo'}
            await db.expert_reviews.update_one({'id': review['id']}, {'$setOnInsert': review}, upsert=True)
            await db.advisories.update_one({'id': identifier}, {'$set': {'status': 'verified', 'expert_recommendation': recommendation, 'expert_name': expert['profile']['name'], 'expert_review_id': review['id'], 'monitoring_eligible': True, 'auto_training': False}})