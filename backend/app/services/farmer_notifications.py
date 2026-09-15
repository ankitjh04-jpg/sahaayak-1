from ..db import db
from ..security.auth import stamp

async def notify_review(case, review):
    status = 'needs_information' if review['decision'] == 'needs_information' else 'verified'
    doc = {'id': review['id'], 'owner': case['owner'], 'advisory_id': case['id'], 'review_id': review['id'], 'title': 'Your expert has responded', 'message': f'{review["expert_name"]} reviewed your {case["crop"]} advisory.', 'crop': case['crop'], 'input_type': case['inputs']['input_type'], 'question': case['title'], 'status': status, 'created_at': review['created_at'], 'read_at': None}
    await db.notifications.update_one({'id': doc['id']}, {'$setOnInsert': doc}, upsert=True)
    await db.expert_reviews.update_one({'id': review['id']}, {'$set': {'notification_sent': True}})

async def repair_notifications():
    async for review in db.expert_reviews.find({'notification_sent': {'$ne': True}}, {'_id': 0}):
        case = await db.advisories.find_one({'id': review['advisory_id']}, {'_id': 0})
        if case:
            await notify_review(case, review)