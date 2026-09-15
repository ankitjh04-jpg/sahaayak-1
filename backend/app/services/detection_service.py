from ..integrations.adapters import vision_adapter
async def detect(inputs): return await vision_adapter.detect(inputs.get('upload_ids', []))