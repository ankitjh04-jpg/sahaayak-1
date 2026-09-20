"""Retrieval from the Sahaayak disease knowledge base (RAG-ready JSON).

Indexed by dataset_label so retrieval is exact after ML classification
(crop + disease first, per the knowledge base's own rules). Falls back to
alias/crop-disease matching if the exact label is not found.
"""
import json
from ..config import BACKEND_ROOT

_PATH = BACKEND_ROOT / 'app' / 'ml' / 'rag_knowledge.json'
_data: dict | None = None
_index: dict = {}


def _load():
    global _data
    if _data is None:
        with open(_PATH, encoding='utf-8') as f:
            _data = json.load(f)
        for entry in _data['diseases']:
            for key in [entry['dataset_label'], *entry.get('aliases', [])]:
                _index[key.lower()] = entry
    return _data


def meta() -> dict:
    d = _load()
    return {'name': d['knowledge_base'], 'version': d['version'], 'sources': d['sources']}


def retrieve(class_label: str | None) -> dict | None:
    """Return the matched disease entry, shaped for the UI, or None."""
    if not class_label:
        return None
    entry = _index.get(class_label.lower())
    if not entry:
        # secondary lookup: crop + disease words from the model label
        parts = class_label.replace('_', ' ').lower().split()
        for candidate in _index.values():
            hay = (candidate['crop'] + ' ' + candidate['disease']).lower()
            if all(p in hay for p in parts):
                entry = candidate
                break
    if not entry:
        return None
    return {
        'matched': entry['dataset_label'],
        'crop': entry['crop'],
        'disease': entry['disease'],
        'disease_type': entry.get('disease_type'),
        'symptoms': entry['symptoms'],
        'management': entry['management'],
        'treatment': entry.get('chemical_management', []),
        'fertilizer': entry['fertilizer_guidance'],
        'prevention': entry['prevention'],
        'sources': entry['sources'],
        'safety_note': entry.get('safety_note'),
        'last_verified': entry.get('last_verified'),
    }
