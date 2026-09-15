from fastapi import APIRouter, Depends
from ..schemas import FieldCreate, Document
from ..security.auth import farmer, stamp, uid, audit
from ..db import db
router = APIRouter()
@router.post('/fields', response_model=Document, status_code=201)
async def create_field(body: FieldCreate, user=Depends(farmer)):
    doc = {**body.model_dump(mode='json'), 'id': uid(), 'owner': user['id'], 'created_at': stamp(), 'updated_at': stamp()}
    await db.fields.insert_one(doc.copy())
    await audit(user['id'], 'field.created', doc['id'])
    return doc
@router.get('/fields', response_model=list[Document])
async def fields(user=Depends(farmer)):
    return await db.fields.find({'owner': user['id']}, {'_id': 0}).sort('created_at', -1).to_list(500)