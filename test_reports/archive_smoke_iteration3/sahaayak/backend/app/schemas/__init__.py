from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
import unicodedata
Language = Literal['en', 'hi', 'pa']

class Document(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: str

class PhoneRequest(BaseModel):
    phone: str = Field(pattern=r'^\+[1-9]\d{7,14}$')
    language: Language = 'en'

class OtpRequest(PhoneRequest):
    # Optional only for backwards-compatible API clients; the login UI requires it.
    name: str | None = Field(None, max_length=80)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value):
        if value is None:
            return None
        value = unicodedata.normalize('NFC', value)
        allowed_punctuation = " .'-’\u200c\u200d"
        if any(not (unicodedata.category(ch).startswith(('L', 'M')) or ch in allowed_punctuation) for ch in value):
            raise ValueError('Use letters, spaces, apostrophes, hyphens or periods for your name')
        value = ' '.join(value.split())
        if len(value) < 2 or not any(ch.isalpha() for ch in value):
            raise ValueError('Enter your name using at least two characters')
        return value

class OtpVerify(PhoneRequest):
    code: str = Field(pattern=r'^\d{6}$')

class DemoRequest(BaseModel):
    role: Literal['farmer', 'expert'] = 'farmer'

class ExpertLogin(BaseModel):
    email: str = Field(min_length=5, max_length=254, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    password: str = Field(min_length=1, max_length=256)

class AadhaarDemoRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Soil(BaseModel):
    ph: float | None = Field(None, ge=0, le=14)
    nitrogen: float | None = Field(None, ge=0, le=2000)
    phosphorus: float | None = Field(None, ge=0, le=2000)
    potassium: float | None = Field(None, ge=0, le=2000)

class FieldCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    crop: Literal['Wheat', 'Rice', 'Cotton', 'Maize', 'Mustard', 'Vegetables']
    location: str = Field(min_length=2, max_length=160)
    acreage: float = Field(gt=0, le=100000)
    sowing_date: date
    soil_profile: Soil = Field(default_factory=Soil)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    @model_validator(mode='after')
    def validate_dates(self):
        if self.sowing_date > date.today():
            raise ValueError('Sowing date cannot be in the future')
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError('Provide both map coordinates')
        return self

class AdvisoryCreate(BaseModel):
    field_id: str
    query: str = Field('', max_length=4000)
    input_type: Literal['text', 'image', 'voice', 'soil'] = 'text'
    upload_ids: list[str] = Field(default_factory=list, max_length=5)
    language: Language = 'en'
    idempotency_key: str = Field(min_length=8, max_length=100)
    @model_validator(mode='after')
    def require_content(self):
        self.query = self.query.strip()
        if len(self.query) < 8 and not self.upload_ids:
            raise ValueError('Describe your concern in at least 8 characters or attach a file')
        return self

class Feedback(BaseModel):
    helpful: bool
    comment: str = Field('', max_length=1000)

class ReviewCreate(BaseModel):
    decision: Literal['validated', 'edited', 'needs_information']
    recommendation: str = Field(min_length=20, max_length=5000)
    rationale: str = Field(min_length=10, max_length=2000)
    source_id: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    advisory_id: str | None = None
    mode: str = 'demo'

class HealthResponse(BaseModel):
    status: str
    database: str
    mode: str
    adapters: dict[str, str]