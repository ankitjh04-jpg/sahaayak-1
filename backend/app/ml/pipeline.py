"""Local crop-condition pipeline: Crop_pred_model.h5 (128×128 RGB → 35 classes).

The model is loaded once (lazily, thread-safe) and reused for every request.
Preprocessing: resize to 128×128, RGB, pixel values scaled to 0–1 (the standard
Keras ImageDataGenerator `rescale=1./255` convention the model was trained with).
"""
import asyncio
import io
import logging
import threading
from ..config import BACKEND_ROOT

MODEL_PATH = BACKEND_ROOT / 'app' / 'models' / 'Crop_pred_model.h5'
IMAGE_SIZE = (128, 128)
_model = None
_load_lock = threading.Lock()


def _load():
    global _model
    if _model is None:
        with _load_lock:
            if _model is None:
                logging.getLogger('tensorflow').setLevel(logging.ERROR)
                import tensorflow as tf
                _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    return _model


def warmup() -> dict:
    """Load the model into memory so the first prediction is fast."""
    model = _load()
    return {'model': MODEL_PATH.name, 'input_size': list(IMAGE_SIZE), 'output_classes': int(model.output_shape[-1])}


def predict_image(data: bytes) -> dict:
    import numpy as np
    from PIL import Image
    from . import labels
    model = _load()
    try:
        image = Image.open(io.BytesIO(data)).convert('RGB')
    except Exception:
        raise ValueError('IMAGE_UNREADABLE')
    image = image.resize(IMAGE_SIZE)
    # The model was trained with cv2.imread (BGR channel order), so keep BGR.
    batch = np.asarray(image, dtype='float32')[..., ::-1] / 255.0
    batch = np.ascontiguousarray(batch)
    batch = np.expand_dims(batch, axis=0)
    scores = model.predict(batch, verbose=0)[0]
    order = np.argsort(scores)[::-1]

    def entry(index: int) -> dict:
        return {'class_id': int(index), 'class_label': labels.label(int(index), int(scores.size)), 'probability': float(scores[index])}

    best = entry(int(order[0]))
    from . import knowledge
    second = float(scores[order[1]]) if scores.size > 1 else 0.0
    guidance = knowledge.guidance_for(best['class_label'] or '', best['probability'], second)
    return {
        'status': 'predicted',
        'mode': 'local_keras_cnn',
        'model': MODEL_PATH.name,
        'input_size': list(IMAGE_SIZE),
        'output_classes': int(scores.size),
        'labels_configured': labels.configured(int(scores.size)),
        'preprocessing': 'resize 128×128 BGR (cv2 order) · pixel values scaled to 0–1',
        'class_id': best['class_id'],
        'class_label': best['class_label'],
        'confidence': best['probability'],
        'top_predictions': [entry(int(i)) for i in order[:3]],
        'guidance': guidance,
    }


async def predict_upload(data: bytes) -> dict:
    return await asyncio.to_thread(predict_image, data)
