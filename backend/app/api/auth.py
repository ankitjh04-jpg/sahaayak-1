import asyncio
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo.errors import DuplicateKeyError
from ..schemas import OtpRequest, OtpVerify, DemoRequest, Document, ExpertLogin, ExpertRegister, AadhaarDemoRequest
from ..security.auth import now, stamp, uid, digest, session, current_user, rate_limit, audit, bearer
from ..security.passwords import verify_password, hash_password, DUMMY_HASH
from ..integrations.otp import get_otp_adapter, otp_mode
from ..db import db
from ..config import DEMO_MODE, FARMER_PHONE, EXPERT_PHONE
router = APIRouter()

async def get_or_create(phone, language='en'):
    user = await db.users.find_one({'phone': phone}, {'_id': 0})
    if not user:
        user = {'id': uid(), 'phone': phone, 'role': 'farmer', 'language': language, 'profile': {'name': 'Gurpreet Singh' if phone == FARMER_PHONE else 'Farmer', 'location': 'Ludhiana, Punjab' if phone == FARMER_PHONE else ''}, 'created_at': stamp(), 'updated_at': stamp()}
        try: await db.users.insert_one(user.copy())
        except DuplicateKeyError: user = await db.users.find_one({'phone': phone}, {'_id': 0})
    return user

@router.post('/auth/otp/request')
async def request_otp(body: OtpRequest, request: Request):
    await rate_limit(f'otp-ip:{request.client.host}', 20, 300)
    await rate_limit(f'otp-phone:{body.phone}', 5, 300)
    if body.phone == EXPERT_PHONE or await db.users.find_one({'phone': body.phone, 'role': 'expert'}, {'_id': 0, 'id': 1}):
        raise HTTPException(403, 'Please use expert sign-in for this account.')
    prior = await db.otps.find_one({'phone': body.phone}, {'_id': 0})
    if prior and prior.get('sent_at') and (now() - prior['sent_at'].replace(tzinfo=now().tzinfo)).total_seconds() < 30:
        raise HTTPException(429, 'Please wait 30 seconds before requesting another code.', headers={'Retry-After': '30'})
    result = await get_otp_adapter().send(body.phone)
    challenge = {'phone': body.phone, 'challenge_id': uid(), 'provider': otp_mode(), 'verification_sid': result.get('verification_sid'), 'attempts': 0, 'expires_at': now() + timedelta(minutes=5), 'sent_at': now(), 'language': body.language, 'pending_name': body.name}
    # Do not store either live or demo OTP digits in MongoDB.
    await db.otps.replace_one({'phone': body.phone}, challenge.copy(), upsert=True)
    return {key: value for key, value in {**result, 'expires_in': 300, 'resend_after': 30}.items() if key != 'verification_sid'}

@router.post('/auth/otp/verify')
async def verify_otp(body: OtpVerify, request: Request):
    await rate_limit(f'verify:{request.client.host}', 30, 300)
    challenge = await db.otps.find_one_and_update({'phone': body.phone, 'expires_at': {'$gt': now()}, 'attempts': {'$lt': 5}, 'provider': otp_mode(), 'challenge_id': {'$exists': True}}, {'$inc': {'attempts': 1}}, return_document=True, projection={'_id': 0})
    if not challenge: raise HTTPException(400, 'OTP expired or attempt limit reached. Request a new code.')
    if not await get_otp_adapter().check(body.phone, body.code, challenge):
        raise HTTPException(400, 'Incorrect OTP. Please try again.')
    consumed = await db.otps.delete_one({'phone': body.phone, 'challenge_id': challenge['challenge_id']})
    if not consumed.deleted_count: raise HTTPException(400, 'OTP has already been used or replaced')
    user = await get_or_create(body.phone, challenge['language'])
    if user['role'] != 'farmer': raise HTTPException(403, 'Please use expert sign-in')
    name = challenge.get('pending_name')
    profile = {**user['profile'], 'phone_verified': challenge['provider'] == 'live'}
    if name is not None:
        profile.update({'name': name, 'name_source': 'self_reported'})
    updated_at = stamp()
    await db.users.update_one({'id': user['id'], 'role': 'farmer'}, {'$set': {'profile': profile, 'language': challenge['language'], 'updated_at': updated_at}})
    user = {**user, 'profile': profile, 'language': challenge['language'], 'updated_at': updated_at}
    await audit(user['id'], 'auth.otp_verified', user['id'], {'provider': challenge['provider']})
    return await session(user, auth_method='twilio_verify' if challenge['provider'] == 'live' else 'demo_otp')

@router.post('/auth/expert/login')
async def expert_login(body: ExpertLogin, request: Request):
    email = body.email.strip().lower()
    await rate_limit(f'expert-login-ip:{request.client.host}', 20, 300)
    await rate_limit(f'expert-login:{digest(email)}', 8, 300)
    user = await db.users.find_one({'email': email, 'role': 'expert'}, {'_id': 0})
    if not user and DEMO_MODE and not await db.users.find_one({'email': email}, {'_id': 0, 'id': 1}):
        name = email.split('@', 1)[0].replace('.', ' ').replace('_', ' ').strip().title()[:80] or 'Agricultural Expert'
        user = {'id': uid(), 'email': email, 'role': 'expert', 'language': 'en', 'profile': {'name': name, 'location': '', 'name_source': 'demo_login'}, 'password_hash': hash_password(body.password), 'disabled': False, 'created_at': stamp(), 'updated_at': stamp()}
        await db.users.insert_one(user.copy())
        await audit(user['id'], 'auth.expert_registered', user['id'], {'mode': 'demo_login'})
    valid = await asyncio.to_thread(verify_password, body.password, user.get('password_hash', DUMMY_HASH) if user else DUMMY_HASH)
    if not user or not valid or user.get('disabled'):
        raise HTTPException(401, 'Invalid expert email or password')
    await audit(user['id'], 'auth.expert_login', user['id'])
    return await session(user, auth_method='expert_password')

@router.post('/auth/expert/register')
async def expert_register(body: ExpertRegister, request: Request):
    if not DEMO_MODE:
        raise HTTPException(404, 'Expert registration is disabled')
    email = body.email.strip().lower()
    await rate_limit(f'expert-register-ip:{request.client.host}', 5, 300)
    if await db.users.find_one({'email': email}, {'_id': 0, 'id': 1}):
        raise HTTPException(409, 'An expert account with this email already exists. Sign in instead.')
    user = {'id': uid(), 'email': email, 'role': 'expert', 'language': 'en', 'profile': {'name': body.name.strip(), 'location': '', 'name_source': 'self_reported'}, 'password_hash': hash_password(body.password), 'disabled': False, 'created_at': stamp(), 'updated_at': stamp()}
    await db.users.insert_one(user.copy())
    await audit(user['id'], 'auth.expert_registered', user['id'])
    return await session(user, auth_method='expert_password')

@router.post('/auth/demo')
async def demo(body: DemoRequest, request: Request):
    if not DEMO_MODE: raise HTTPException(404)
    if body.role != 'farmer': raise HTTPException(403, 'Expert access requires email and password')
    await rate_limit(f'demo:{request.client.host}', 60, 60)
    return await session(await get_or_create(FARMER_PHONE), auth_method='demo_farmer')

@router.post('/auth/aadhaar/demo')
async def aadhaar_demo(body: AadhaarDemoRequest, request: Request):
    if not DEMO_MODE: raise HTTPException(404)
    await rate_limit(f'aadhaar-demo:{request.client.host}', 20, 60)
    return {'status': 'demo_complete', 'verified': False, 'mode': 'demo', 'message': 'Demo check complete. Aadhaar has NOT been verified. No Aadhaar number is collected.'}

@router.post('/auth/logout')
async def logout(user=Depends(current_user), credentials=Depends(bearer)):
    await db.sessions.delete_one({'token_hash': digest(credentials.credentials)})
    return {'status': 'signed_out'}

@router.get('/me', response_model=Document)
async def me(user=Depends(current_user)): return user