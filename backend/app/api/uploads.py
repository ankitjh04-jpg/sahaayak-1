import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError
from ..security.auth import current_user, farmer, uid, stamp, rate_limit
from ..schemas import Document
from ..db import db
from ..config import MAX_UPLOAD_BYTES
from ..integrations.adapters import object_store
router = APIRouter()
SIGNATURES = {
 'image/jpeg': lambda b: b.startswith(b'\xff\xd8\xff'), 'image/png': lambda b: b.startswith(b'\x89PNG\r\n\x1a\n'),
 'image/webp': lambda b: b[:4] == b'RIFF' and b[8:12] == b'WEBP', 'application/pdf': lambda b: b.startswith(b'%PDF-'),
 'audio/wav': lambda b: b[:4] == b'RIFF' and b[8:12] == b'WAVE',
 'audio/mpeg': lambda b: b.startswith(b'ID3') or (len(b) > 1 and b[0] == 255 and b[1] & 224 == 224),
 'audio/webm': lambda b: b.startswith(b'\x1aE\xdf\xa3'), 'audio/ogg': lambda b: b.startswith(b'OggS'), 'audio/mp4': lambda b: b[4:8] == b'ftyp'}
@router.post('/uploads', response_model=Document, status_code=201)
async def upload(file: UploadFile = File(...), user=Depends(farmer)):
    await rate_limit(f'upload:{user["id"]}', 30, 60)
    media = (file.content_type or '').split(';')[0]
    if media not in SIGNATURES: raise HTTPException(415, 'Use JPG, PNG, WebP, PDF, WAV, MP3, M4A, OGG, or WebM')
    data = bytearray()
    while chunk := await file.read(65536):
        data.extend(chunk)
        if len(data) > MAX_UPLOAD_BYTES: raise HTTPException(413, 'File exceeds the 10 MB limit')
    if not data or not SIGNATURES[media](bytes(data[:32])): raise HTTPException(415, 'File content does not match its type, or the file is empty')
    checksum = hashlib.sha256(data).hexdigest()
    existing = await db.uploads.find_one({'owner': user['id'], 'checksum': checksum}, {'_id': 0, 'object_key': 0})
    if existing: return {**existing, 'duplicate': True}
    identifier = uid()
    await object_store.put(identifier, bytes(data))
    doc = {'id': identifier, 'owner': user['id'], 'object_key': identifier, 'filename': (file.filename or 'attachment')[:180], 'type': media, 'checksum': checksum, 'size': len(data), 'processing_status': 'stored', 'created_at': stamp(), 'storage_mode': 'private_local_demo'}
    try: await db.uploads.insert_one(doc.copy())
    except DuplicateKeyError:
        object_store.path(identifier).unlink(missing_ok=True)
        return await db.uploads.find_one({'owner': user['id'], 'checksum': checksum}, {'_id': 0, 'object_key': 0})
    return {k: v for k, v in doc.items() if k != 'object_key'}
@router.get('/uploads/{identifier}/content')
async def download(identifier: str, user=Depends(current_user)):
    doc = await db.uploads.find_one({'id': identifier}, {'_id': 0})
    if not doc: raise HTTPException(404, 'Attachment not found')
    if doc['owner'] != user['id']:
        allowed = user['role'] == 'expert' and await db.advisories.find_one({'expert_access': True, 'inputs.upload_ids': identifier}, {'_id': 0})
        if not allowed: raise HTTPException(404, 'Attachment not found')
    if not object_store.path(doc['object_key']).exists(): raise HTTPException(404, 'File is no longer available')
    return FileResponse(object_store.path(doc['object_key']), media_type=doc['type'], filename=doc['filename'], headers={'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})