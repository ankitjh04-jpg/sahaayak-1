from fastapi import APIRouter, Depends, HTTPException
from ..db import db
from ..security.auth import current_user, stamp
from ..schemas import Document
router = APIRouter()

@router.get('/notifications')
async def notifications(user=Depends(current_user)):
    items = await db.notifications.find({'owner': user['id']}, {'_id': 0}).sort('created_at', -1).to_list(100)
    unread = await db.notifications.count_documents({'owner': user['id'], 'read_at': None})
    return {'items': [Document(**item).model_dump() for item in items], 'unread_count': unread}

@router.post('/notifications/read-all')
async def read_all(user=Depends(current_user)):
    await db.notifications.update_many({'owner': user['id'], 'read_at': None}, {'$set': {'read_at': stamp()}})
    return {'status': 'read'}

@router.post('/notifications/{identifier}/read')
async def read(identifier: str, user=Depends(current_user)):
    result = await db.notifications.update_one({'id': identifier, 'owner': user['id']}, {'$set': {'read_at': stamp()}})
    if not result.matched_count: raise HTTPException(404, 'Notification not found')
    return {'status': 'read'}