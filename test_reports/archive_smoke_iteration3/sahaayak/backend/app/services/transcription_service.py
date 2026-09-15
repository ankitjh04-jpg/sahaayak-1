from ..integrations.adapters import transcription_adapter
async def transcribe(inputs):
    if inputs['input_type'] != 'voice': return None
    return await transcription_adapter.transcribe(inputs['upload_ids'], inputs['language'])