"""Class-index → label mapping for Crop_pred_model.h5 (35 output classes).

The .h5 file stores neither class names nor indices (verified via its HDF5
metadata), so the exact labels from your training script (model1.py /
prepro.py — e.g. `train_generator.class_indices`, or the alphabetical
ImageDataGenerator directory order) must be filled in below:
index 0 first, then index 1, ... up to index 34.

While this list is empty, predictions are returned as raw class ids with
`labels_configured: false` — no agricultural label is ever invented.
"""
CLASS_LABELS: list[str] = [
    'Cauliflower_Bacterial_Spot_Rot',
    'Cauliflower_Black_Rot',
    'Cauliflower_Downy_Mildew',
    'Cauliflower_Healthy',
    'Cauliflower_Insect_Hole',
    'Cotton_Aphids',
    'Cotton_Bacterial_Blight',
    'Cotton_Curl_Virus',
    'Cotton_Fussarium_Wilt',
    'Cotton_Healthy',
    'Cotton_Powdery_Mildew',
    'Cotton_Target_Spot',
    'Maize_Healthy',
    'Maize_Leaf_Blight',
    'Maize_Leaf_Spot',
    'Maize_Maize_Rust',
    'Maize_Northern_Leaf_Blight',
    'Maize_Streak_Virus',
    'Onion_Busuk_Daun',
    'Onion_Healthy',
    'Onion_Moler',
    'Onion_Trotol',
    'Potato_Early_Blight',
    'Potato_Healthy',
    'Potato_Late_Blight',
    'Rice_Bacterial_Blight',
    'Rice_Blast',
    'Rice_Brown_Spot',
    'Rice_Tungro',
    'Wheat_Brown_Rust',
    'Wheat_Crown_Root_Rot',
    'Wheat_Healthy',
    'Wheat_Loose_Smut',
    'Wheat_Septoria',
    'Wheat_Yellow_Rust',
]


def configured(output_classes: int) -> bool:
    return len(CLASS_LABELS) == output_classes


def label(class_id: int, output_classes: int) -> str | None:
    if configured(output_classes) and 0 <= class_id < len(CLASS_LABELS):
        return CLASS_LABELS[class_id]
    return None
