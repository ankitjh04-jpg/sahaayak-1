from ..db import db
from ..security.auth import stamp, audit
from .detection_service import detect
from .risk_service import assess
from .transcription_service import transcribe
from .rag_service import retrieve, COPY
async def process_advisory(identifier):
    case = await db.advisories.find_one({'id': identifier}, {'_id': 0})
    if not case or case['status'] != 'processing': return
    field = await db.fields.find_one({'id': case['field_id'], 'owner': case['owner']}, {'_id': 0})
    if not field: raise ValueError('FIELD_UNAVAILABLE')
    inputs = case['inputs']
    detections = await detect(inputs)
    risk = await assess(field, inputs)
    transcription = await transcribe(inputs)
    citations = await retrieve(field['crop'], inputs['query'])
    result = {'detections': detections, 'risk': risk, 'transcription': transcription, 'recommendation': COPY[inputs['language']], 'confidence': detections.get('confidence') if detections.get('status') == 'predicted' else None, 'confidence_label': f"{detections['confidence'] * 100:.1f}% model match" if detections.get('status') == 'predicted' else 'Not assessed', 'citations': citations, 'status': 'pending_review', 'expert_access': True, 'missing_inputs': risk['missing_inputs'], 'advisory_type': 'ai_assisted' if detections.get('status') == 'predicted' else 'general', 'assumptions': ['Vision prediction comes from the bundled CNN model (Crop_pred_model.h5) on the uploaded image(s); it is not expert-verified.'] if detections.get('status') == 'predicted' else ['Crop, location and symptoms are farmer-reported, not independently verified.', 'No live vision, weather, soil OCR, or language-model inference was performed.'], 'normalized_query': inputs['query'], 'updated_at': stamp(), 'monitoring_eligible': False, 'auto_training': False}
    await db.advisories.update_one({'id': identifier, 'status': 'processing'}, {'$set': result})
    await audit('system', 'advisory.escalated', identifier, {'reason': 'Unverified inputs; general guidance only', 'source_ids': [s['id'] for s in citations]})