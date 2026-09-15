import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..security.auth import current_user, rate_limit
from ..ml import pipeline

router = APIRouter()
SIGNATURES = {'image/jpeg': lambda b: b.startswith(b'\xff\xd8\xff'), 'image/png': lambda b: b.startswith(b'\x89PNG\r\n\x1a\n'), 'image/webp': lambda b: b[:4] == b'RIFF' and b[8:12] == b'WEBP'}

@router.post('/predict')
async def predict(file: UploadFile = File(...), user=Depends(current_user)):
    await rate_limit(f'predict:{user["id"]}', 30, 60)
    media = (file.content_type or '').split(';')[0]
    if media not in SIGNATURES: raise HTTPException(415, 'Use JPG, PNG, or WebP')
    data = await file.read()
    if not data or not SIGNATURES[media](data[:32]): raise HTTPException(415, 'File content does not match its type, or the file is empty')
    try: result = await pipeline.predict_upload(data)
    except ValueError: raise HTTPException(415, 'Image could not be decoded')
    except FileNotFoundError: raise HTTPException(503, 'Crop model is not installed')
    return {**result, 'disease': result['class_label'] or f"Class #{result['class_id']}", 'confidence_pct': round(result['confidence'] * 100, 2)}