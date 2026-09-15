import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..db import db
bearer = HTTPBearer(auto_error=False)
def now(): return datetime.now(timezone.utc)
def stamp(): return now().isoformat()
def uid(): return str(uuid4())
def digest(value): return hashlib.sha256(value.encode()).hexdigest()

async def audit(actor, action, resource, detail=None):
    await db.audit_logs.insert_one({'id': uid(), 'actor': actor, 'action': action, 'resource': resource, 'detail': detail or {}, 'created_at': stamp()})

async def rate_limit(key, limit=12, seconds=60):
    bucket = int(now().timestamp()) // seconds
    item = await db.rate_limits.find_one_and_update({'_id': f'{key}:{bucket}'}, {'$inc': {'count': 1}, '$setOnInsert': {'expires_at': now() + timedelta(seconds=seconds * 2)}}, upsert=True, return_document=True)
    if item['count'] > limit:
        raise HTTPException(429, 'Too many requests. Please try again shortly.', headers={'Retry-After': str(seconds)})

def public_user(user):
    return {key: value for key, value in user.items() if key not in ('_id', 'password_hash', 'password_salt', 'disabled')}

async def session(user, auth_method='phone_otp'):
    token = secrets.token_urlsafe(48)
    await db.sessions.insert_one({'token_hash': digest(token), 'user_id': user['id'], 'auth_method': auth_method, 'expires_at': now() + timedelta(hours=12)})
    return {'access_token': token, 'token_type': 'bearer', 'user': public_user(user), 'auth_method': auth_method}

async def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials: raise HTTPException(401, 'Please sign in')
    entry = await db.sessions.find_one({'token_hash': digest(credentials.credentials), 'expires_at': {'$gt': now()}}, {'_id': 0})
    if not entry: raise HTTPException(401, 'Session expired. Please sign in again.')
    user = await db.users.find_one({'id': entry['user_id']}, {'_id': 0})
    if not user or user.get('disabled'): raise HTTPException(401, 'Account unavailable')
    if user['role'] == 'expert' and (entry.get('auth_method') != 'expert_password' or not user.get('password_hash')):
        raise HTTPException(401, 'Please sign in with your expert credentials')
    return public_user(user)

async def farmer(user=Depends(current_user)):
    if user['role'] != 'farmer': raise HTTPException(403, 'Farmer access required')
    return user

async def expert(user=Depends(current_user)):
    if user['role'] != 'expert': raise HTTPException(403, 'Expert access required')
    return user

async def owned_advisory(identifier, user):
    query = {'id': identifier}
    if user['role'] != 'expert': query['owner'] = user['id']
    else: query['expert_access'] = True
    result = await db.advisories.find_one(query, {'_id': 0})
    if not result: raise HTTPException(404, 'Case not found')
    return result