# Sahaayak — SIH26131 Technical Document

Version 1.0 · 8 September 2026 · Credential-free demonstration

## 1. Purpose and operating boundaries

Sahaayak implements **Detect → Predict → Advise → Validate → Monitor** for farmers and agricultural experts. Detection and prediction stages validate data availability; they do not manufacture disease labels or risk scores. The first build has deliberately **no live AI, OTP, weather, vision, soil-OCR, or messaging credentials**.

The working application has real authentication sessions, records, upload bytes, queued jobs, role checks, expert decisions, feedback, and local offline recovery. Public demo sessions and simulated OTP are not production identity verification. Browser speech synthesis is a device capability, not OpenAI speech output.

## 2. Architecture

```text
React 19 + TypeScript + React Router + shadcn/Radix
  │ fetch: REACT_APP_BACKEND_URL + /api/v1
  │ IndexedDB offline queue / per-owner cached view data
  │ Service worker: shell/static assets only; no API/OSM tile cache
  ▼
FastAPI app.main:app (0.0.0.0:8001)
  ├─ API: auth / fields / advisories / uploads / experts / health
  ├─ security: expiring opaque sessions, roles, ownership, rate limits, audit
  ├─ services: detection, risk, retrieval, transcription, notification worker
  ├─ adapter protocols: OTP, vision, weather, transcription, WhatsApp, object store
  └─ MongoDB via Motor (MONGO_URL only)
       users / fields / advisories / expert_reviews / uploads
       knowledge_sources / jobs / sessions / otps / rate_limits / audit_logs
  ▼
Private local object store (demo adapter): bytes on disk, metadata in MongoDB
```

The repository root itself is `sahaayak/`. In the supplied workspace it is `/app`; there is no duplicate nested source tree. `backend/server.py` and `frontend/src/App.js` are compatibility entry points. All new app screens and client logic are TypeScript.

### Folder tree

```text
.
├── frontend/
│   ├── src/
│   │   ├── app/{context.tsx,offlineRegistration.ts}
│   │   ├── api/{client.ts,auth.ts,advisories.ts}
│   │   ├── components/{Layout,FieldCard,FieldForm,FarmMap,AttachmentInput,AdvisoryContent,shared}.tsx
│   │   ├── components/ui/   # existing shadcn controls + TypeScript declarations
│   │   ├── pages/{LoginPage,FarmerDashboard,FieldsPage,NewAdvisoryPage,
│   │   │          AdvisoryResultPage,HistoryPage,ExpertDashboard,CaseReviewPage,KnowledgePage}.tsx
│   │   ├── hooks/{useData.ts,offline.ts}
│   │   ├── types/index.ts
│   │   ├── styles/{tokens.css,global.css}
│   │   └── main.tsx
│   ├── public/{index.html,sw.js,images/wheat-hero.jpg}
│   ├── {package.json,yarn.lock,tsconfig.json,craco.config.js}
│   └── {.env.example,Dockerfile,nginx.conf}
├── backend/
│   ├── app/
│   │   ├── {main.py,config.py,db.py,seed.py}
│   │   ├── api/{auth,fields,advisories,uploads,experts,health}.py
│   │   ├── schemas/__init__.py
│   │   ├── models/__init__.py
│   │   ├── services/{advisory,detection,risk,rag,transcription,notification}_service.py
│   │   ├── integrations/adapters.py
│   │   ├── security/auth.py
│   │   └── tests/
│   └── {server.py,requirements.txt,.env.example,Dockerfile}
├── docs/SAHAAYAK_TECHNICAL_DOCUMENT.md
├── test_reports/
└── {README.md,docker-compose.yml,.env.example,.gitignore}
```

## 3. Setup and configuration

Prerequisites: Python 3.11+, Node 20+, Yarn 1.22, MongoDB. Linux/macOS commands:

```bash
# Only on a fresh checkout. Do not overwrite preconfigured workspace .env files.
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit STORAGE_ROOT to an absolute private directory writable by your user.
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
# Separate terminal, from repository root:
cd frontend
yarn install --frozen-lockfile
yarn start
```

Managed workspace processes are controlled by supervisor, not additional uvicorn instances. Open the configured external frontend origin. Standalone setup opens `http://localhost:3000`. API reference is at backend `/docs` and schema at `/openapi.json`.

### Environment variables

| Variable | Location | Requirement |
|---|---|---|
| MONGO_URL | backend | Required database URI; existing protected value retained |
| DB_NAME | backend | Required MongoDB database name |
| FRONTEND_ORIGIN | backend | Exact allowed browser origin, no wildcard credential policy |
| CORS_ORIGINS | backend | Legacy template setting retained; FRONTEND_ORIGIN is used by app |
| DEMO_MODE | backend | `true` enables public fixtures/demo session; live OTP not configured |
| DEMO_OTP | backend | Public six-digit simulation code; example `123456` |
| DEMO_FARMER_PHONE | backend | Public farmer fixture identity |
| DEMO_EXPERT_PHONE | backend | Public expert fixture allowlist identity |
| STORAGE_ROOT | backend | Absolute private storage path |
| MAX_UPLOAD_BYTES | backend | `10485760` in the demo (10 MiB) |
| OSM_TILE_URL | backend | Public OSM tile template; returned by `/config` |
| REACT_APP_BACKEND_URL | frontend | Required public backend origin, compiled into frontend |
| COMPOSE_MONGO_URL | root Docker config | Container-reachable MongoDB URI |
| BACKEND_PORT / FRONTEND_PORT | root Docker config | Host ports for Compose |
| PUBLIC_API_ORIGIN | root Docker config | Browser-reachable backend origin at frontend build time |

No provider secret is needed for the demo. `.env*` is ignored except `.env.example`; `.dockerignore` excludes all environment files. Real secrets must not be written to the frontend, source, Git, logs, MongoDB, browser storage, or documentation.

**Exposed key:** revocation must be performed by the owner in the OpenAI console. This repository does not contain or use that credential and cannot revoke it on the owner's behalf. Create a replacement privately before any live integration.

## 4. User journeys

### Farmer

1. Root opens a clearly labeled public demo farmer workspace. `/login` supports phone OTP simulation or demo role selection.
2. Phone request stores a hashed code with a five-minute TTL. Correct verification atomically consumes the challenge and creates a twelve-hour session. Only the server's expert fixture phone is provisioned as expert.
3. Create a field: name, crop, district/village, acreage, past/current sowing date; optional soil pH/N/P/K and paired map coordinates.
4. Submit a typed question or crop image, Soil Health Card (image/PDF), or audio. Record audio for up to 60 seconds. Photos are resized to a 1400px maximum dimension and JPEG quality 0.75 when this reduces size.
5. Server validates ownership and media; persists advisory and job; responds 202. The page polls without blocking the request.
6. Detection returns unavailable, risk returns unknown, speech returns unavailable, and retrieval returns cited general FAO IPM guidance. Missing data, assumptions, and no-diagnosis boundary remain visible. No percentages are invented.
7. All new demo cases enter `pending_review`. Farmer can listen using an installed browser voice, request simulated WhatsApp, and submit helpful/not-helpful feedback.
8. History supports query/crop/status filters. Offline requests and files are saved per owner to IndexedDB and synced on reconnection or next online visit. Users can retry or remove queued items.

### Expert

1. Public demo expert workspace lists escalated cases only. A farmer bearer token cannot access expert APIs.
2. View input, download authorized attachments, see missing data, sources, assumptions, and general guidance.
3. Validate, edit and validate, or request more information. Recommendation, rationale, and verified source are required.
4. Only a pending/needs-information case is atomically eligible for a new decision; stale duplicate reviews receive 409.
5. Decision stores expert identity, previous recommendation, changes, rationale, source metadata, timestamp, and audit event.
6. Verified cases enter monitoring/evaluation. JSON export contains minimal case/crop/status/source IDs, not phone numbers or raw attachments. `auto_training` is always false.

## 5. API contract

All authenticated requests use `Authorization: Bearer <opaque-session-token>`; JSON requests use `Content-Type: application/json`. Collection results exclude MongoDB `_id`; Pydantic response models allow public document fields only. ISO UTC strings are used for application timestamps; MongoDB datetime values are used for expiry indexes.

| Method | Path | Auth | Behavior |
|---|---|---|---|
| POST | /api/v1/auth/otp/request | Public | Simulated OTP, expiry + per-phone/IP throttling |
| POST | /api/v1/auth/otp/verify | Public | One-time challenge verification and session |
| GET | /api/v1/me | User | Current user |
| POST | /api/v1/fields | Farmer | Field create, 201 |
| GET | /api/v1/fields | Farmer | Owner's fields |
| POST | /api/v1/advisories | Farmer | Persist + enqueue, 202, idempotent |
| GET | /api/v1/advisories | Farmer | Owner's history |
| GET | /api/v1/advisories/{id} | Owner/authorized expert | Case plus reviews |
| POST | /api/v1/advisories/{id}/feedback | Owner | Upsert feedback |
| GET | /api/v1/expert/cases | Expert | Escalated review/monitoring cases |
| POST | /api/v1/expert/cases/{id}/review | Expert | Guarded decision + audit |
| POST | /api/v1/uploads | Farmer | Private validated file, multipart `file`, 201 |
| GET | /api/v1/health | Public | Database check, mode, adapter states |
| POST | /api/v1/auth/demo | Demo only | Public fixture session, `{role: farmer|expert}` |
| POST | /api/v1/auth/logout | User | Revokes current session |
| GET | /api/v1/uploads/{id}/content | Owner/authorized expert | Private no-store attachment download |
| POST | /api/v1/advisories/{id}/whatsapp | Owner | Simulated message job, 202 |
| GET | /api/v1/jobs/{id} | Job owner | Persisted status, retries, safe provider error code |
| GET | /api/v1/knowledge-sources | User | Verified general sources |
| GET | /api/v1/weather | User | Explicit no-data fallback |
| GET | /api/v1/config | Public | Demo flag, supported languages, public map template |

### Request and response examples (public demo values only)

```json
// OTP request
{"phone":"+919876543210","language":"en"}
// OTP verification
{"phone":"+919876543210","code":"123456","language":"en"}
// Field create
{"name":"North field","crop":"Wheat","location":"Ludhiana, Punjab","acreage":4.5,"sowing_date":"2026-08-01","soil_profile":{"ph":7.2},"latitude":30.914,"longitude":75.801}
// Advisory create (key must be stable on retry)
{"field_id":"<owned-field-id>","query":"Lower leaves are yellowing over three days","input_type":"text","upload_ids":[],"language":"pa","idempotency_key":"<client-generated-uuid>"}
// 202 response
{"advisory_id":"<uuid>","job_id":"<uuid>","status":"queued","mode":"demo"}
// Expert review
{"decision":"validated","recommendation":"Observe both affected and healthy plants and consult a local expert before treatment.","rationale":"General prevention principles are supported; diagnosis remains unconfirmed.","source_id":"fao-ipm-2026"}
// Feedback
{"helpful":true,"comment":"Clear starting point"}
```

Advisory result includes `inputs`, `normalized_query`, `detections`, `risk`, `recommendation`, `confidence: null`, `confidence_label`, `missing_inputs`, `assumptions`, `citations`, `status`, `expert_access`, `monitoring_eligible`, `auto_training: false`, and timestamps. Structured multilingual advice is a human-authored template, not LLM output. English source titles, technical metadata, seeded text, and several operational labels are intentionally retained; full medical/agricultural translation QA is a future requirement.

Validation errors use 422, missing/unauthorized owner resources use 404, role mismatch 403, missing/expired session 401, rate limit 429, unsupported media 415, too-large media 413, duplicate-conflicting payload or already-reviewed case 409, unavailable database/provider 503 where applicable. The client applies a 25-second timeout and retains form state on failure.

## 6. MongoDB documents and indexes

| Collection | Important fields | Indexes |
|---|---|---|
| users | id, phone, role, language, profile, timestamps | id unique; phone unique |
| fields | id, owner, crop, name, location, acreage, sowing_date, soil_profile, coordinates | id unique; owner + created_at |
| advisories | id, owner, inputs, field, result, citations, status, job_id, idempotency_key | id unique; owner + idempotency_key unique; status + created_at |
| expert_reviews | id, advisory_id, expert_id, previous_recommendation, recommendation, rationale, source, decision | id unique; advisory_id + created_at |
| uploads | id, owner, object_key, filename, type, size, checksum, processing_status | id unique; owner + checksum unique |
| knowledge_sources | id, title, region, crop, publisher, version, excerpt, scope, URL, verified | id unique |
| jobs | id, owner, resource_id, operation, status, retries, provider_error, next_attempt_at, timestamps | id unique; status + next_attempt_at |
| sessions | token_hash, user_id, expires_at | token_hash unique; TTL expires_at |
| otps | phone, code_hash, attempts, expires_at, language | phone unique; TTL expires_at |
| rate_limits | fixed-window composite _id, count, expires_at | default _id unique; TTL expires_at |
| audit_logs | id, actor, action, resource, detail, created_at | id unique |

All joins use string UUIDs or explicit string fixture IDs, not BSON references. Queries returning Mongo-originated data use `{'_id': 0}`. Insert operations use copies to prevent driver-injected `_id` contaminating response payloads. Audit events never contain OTPs, tokens, or provider keys.

## 7. Background jobs, retries, and failure behavior

One asyncio worker atomically claims `queued` jobs and marks them `running`. Advisory processing has a 20-second timeout. Transient failures retry up to three times with exponential delay. Terminal failures set the case to `failed`, with data retained and no fabricated result. Restart returns interrupted running jobs to the queue and repairs a missing job for a processing advisory.

WhatsApp transport deliberately fails with `DEMO_NO_DELIVERY` after three attempts (2s and 4s retry delays), leaving an explicit not-sent state. Raw SDK exception text is not persisted; errors are allowlisted codes. No third-party SMS or WhatsApp call is made. Demo worker is single-process; before multiple replicas, add distributed leases/visibility timeouts and a durable outbox/transaction policy.

## 8. Upload, privacy, and offline rules

- Up to five attachments per case; ten MiB per file. Accepted: JPEG, PNG, WebP, PDF, WAV, MP3, M4A/MP4 audio, OGG, WebM audio.
- MIME allowlist plus magic-byte validation; empty/mismatched files are rejected. Executables, SVG, archives, and unsupported types are rejected. Signature sniffing is not full antivirus or media decoding; add a quarantine scanner for production.
- Random server-generated object keys prevent filename traversal. SHA-256 deduplication is scoped per owner and protected by a unique index; duplicate race files are removed.
- MongoDB stores metadata only. No public static mount exists for uploads; downloads enforce owner or escalated-case expert access and `private, no-store` headers.
- The browser records audio only after permission, stops all microphone tracks on completion/unmount, and caps recording at 60 seconds. Audio is saved, not falsely transcribed.
- Offline IndexedDB records include owner ID, payload, client idempotency key, and files. Only the current owner's queue is synced. The server independently verifies ownership on replay. A failed replay remains available for retry/removal.
- API and OSM tiles are never cached by the service worker. Cached per-owner field/history view data may be stale and is labeled on network failure. Browser storage is not encrypted at rest; use device protection and explicit consent/retention controls for real sensitive data.
- OSM map attribution is visible. Only field coordinates are plotted; no disease hotspot inference. No tile prefetch, bulk download, or offline tile mode.

## 9. Integration replacement instructions

Adapters are protocol-based in `app/integrations/adapters.py`. Replace an adapter factory implementation, not the HTTP contracts. Require timeouts, bounded retries, safe error codes, observability, and real provider tests before enabling it.

### OTP
Replace `DemoOtpAdapter` with the selected provider's send/verify adapter. Live credentials remain backend-only. Remove public `/auth/demo` and fixed-code acceptance; verify provider delivery/challenge IDs; retain TTL, replay prevention, attempt limits and per-IP/per-phone rate limits. Provision experts through trusted administration, never a client-supplied role.

### OpenAI Whisper / structured multilingual advice / optional TTS
After the exposed key is revoked, privately configure `OPENAI_API_KEY`. Implement `TranscriptionAdapter` with Whisper (`whisper-1`) or an approved current transcription model. Validate audio, consent, language, and timeout. Never invent transcript text on provider failure. Add a structured generation adapter with strict Pydantic schema validation, trusted source retrieval, language validation, and a pesticide safety filter. Structured response must preserve null diagnosis/confidence where evidence is absent. Add TTS through an authorized private audio endpoint; browser read-aloud remains an optional fallback. Consult official current OpenAI documentation before implementing live SDK calls.

### Vision
Replace `NoDataVisionAdapter` with a tested CNN/transfer-learning or YOLO service. Report calibration, label ontology/model version, image quality, uncertainty, out-of-domain detection, and evidence; use abstention for unclear images. Never promote demo fixture results into real observed diagnosis.

### Risk/weather
Replace `NoDataWeatherAdapter` with a provider that returns observation timestamps, location coverage, units, cache age, and stale/no-data flags. Risk adapter must validate feature schema and source age before applying deterministic agronomic rules or Random Forest/XGBoost. If weather/crop/location are missing or stale, abstain rather than fabricate a score. Current risk adapter is data-completeness-only and has no forecasting model.

### RAG
Current retrieval is a curated FAO general-source lookup. Add authorized, verified local agricultural documents to `knowledge_sources` with region/crop/version/page citation metadata. Ingestion must quarantine documents and require expert verification before indexing. Add chunk IDs, checksums and embeddings only after approval. Treat retrieved text as evidence, never tool instructions. Do not use FAO general IPM prose as authority for a pesticide dosage; dosage requires the applicable verified local label and qualified review.

### WhatsApp / Twilio
Implement `WhatsAppAdapter.send` using privately configured Twilio account/auth credentials and approved sender. Require recipient consent/template compliance, idempotency, callback signature validation, safe provider errors, exponential backoff with jitter, and terminal failed-delivery state. Do not label acceptance as delivery; only verified delivery callbacks can do that.

### Object storage
Replace `LocalPrivateObjectStore` with S3-compatible private storage. Preserve random object keys, per-owner checks, checksums, encryption, retention policy, and authorized short-lived access. Never store presigned secrets permanently in MongoDB or send backend credentials to React. Move disk bytes to a private bucket via a separately audited migration.

## 10. Agricultural safety

- General advice is prominently labeled. Seeded expert validation is visibly a demonstration and never confirms a diagnosis.
- No uncertain disease, nutrient deficiency, yield, pesticide, fertilizer, or weather claim is guaranteed.
- Missing inputs, assumptions, diagnostic confidence unavailability, sources, and expert status are always shown.
- Current source library supports general ecological/IPM principles only. Review API rejects common numerical dosage/unit patterns; this is a guardrail, not a substitute for expert label verification or a complete multilingual safety classifier.
- Verified cases are evaluation/monitoring data, not automatic training data. Explicit governance, anonymization, consent, quality checks, and separate approval are necessary for future model training.

## 11. Test plan and commands

```bash
cd frontend
yarn tsc --noEmit
yarn build
cd ../backend
pytest app/tests -q
```

Automated QA creates reports under `test_reports/`. Use the configured public backend origin for end-to-end calls, not an unrelated localhost service. Browser QA uses desktop 1920×800 and mobile 390×844. The full SIH scenario:

1. Load seeded dashboard and confirm wheat image, real Mongo counts, no-data weather, role switch, and mobile navigation.
2. OTP request, correct verify, wrong code, expiry, five-attempt lockout, reused code rejection, invalid phone, unsupported language, and rate-limit response.
3. Create a field with optional pH/N/P/K; reject negative acreage, invalid pH, future sowing, unmatched coordinates, missing required data.
4. Submit text, image, PDF, and voice; test duplicate uploads, MIME spoofing, empty/oversized files, and object authorization.
5. Confirm 202 job ID; poll through safe general result; confirm null confidence/risk, no fabricated diagnosis/transcript, source and missing inputs.
6. Repeat idempotency key unchanged: one advisory only. Repeat with changed payload: 409.
7. Farmer cannot access expert routes or another farmer's field, case, upload, or job.
8. Expert opens escalated case, validates/edits with rationale + verified citation, and decision appears in farmer result/history and monitoring. Duplicate review receives 409.
9. Feedback persists. WhatsApp shows queued retries then explicitly not sent. Unsupported browser voice displays an honest fallback.
10. Offline submission with files survives reload and syncs only for its owner; network timeout preserves state; failed sync remains visible. No horizontal overflow, including long unbroken query/field text.
11. Language selector updates primary UI; submitted Hindi/Punjabi response templates render correctly. Official citation remains in source language.
12. Export monitoring JSON; verify no phone/raw attachment leakage and no automatic training.

## 12. Container/release steps

```bash
# From root on a fresh checkout:
cp .env.example .env
cp backend/.env.example backend/.env
# Set browser origin, public API origin, storage path and DB settings appropriately.
docker compose up --build -d
docker compose logs backend
```

Frontend uses a Node build stage and nginx SPA fallback; backend image runs as a non-root user and binds to port 8001. MongoDB and private objects use named volumes. Compose configuration is provided; container execution depends on a Docker-enabled host. Verify migrations/indexes, health endpoint, real-origin CORS, TLS, route fallbacks, persistent volume backup/restore and worker recovery before a release. Multi-instance workers and production delivery are not asserted by the demo.

Before real farmer use: revoke prior exposed secrets; replace demo auth/providers; approve region-specific citations and translations; add consent/data retention, antivirus, distributed job leases, multi-document transaction/outbox guarantees, governance approval, accessibility audit, and qualified agronomic validation. Run integration/failure tests against each actual provider. Do not enable automatic model training as part of rollout.

## 13. Source and asset provenance

- FAO, *Integrated Pest Management*, official web page: https://www.fao.org/pest-and-pesticide-management/ipm/integrated-pest-management/en/ . Retrieved for the demo; paraphrases are scoped to general principles, not diagnosis/dosage.
- Wheat photograph: Unsplash image `photo-1559668772-786155c8cdf2`, downloaded to the local public asset directory for lower repeated bandwidth. Decorative/reference image only, never analyzed as a farmer's upload.
- Leaflet/OpenStreetMap attribution remains visible on maps.

## 14. Farmer identity and native camera addition — 9 September 2026

### Agreed scope

The requested next integrations are an authorized Aadhaar verification provider, Twilio phone SMS OTP, Google Maps geolocation, and OpenWeather. The final user instruction was to build farmer-name and camera functionality now and keep live integrations disconnected pending private credentials. The Aadhaar provider's actual name/API documentation is still required. No Aadhaar number, document, or OTP is collected by this addition. A self-reported name must not be interpreted as Aadhaar-verified identity.

### Name contract and safeguards

`POST /api/v1/auth/otp/request` now accepts optional `name` alongside `phone` and `language`; the current login UI requires the name. Optionality preserves existing API clients. Names accept Unicode letters/marks, spaces, apostrophes, periods, hyphens and script joiners. They are NFC-normalized and internal spaces are collapsed; blank, numeric-only, control-character/markup names and names over 80 characters are rejected.

```json
{"phone":"+919876543210","language":"en","name":"Gurpreet Singh"}
```

The name is held as `pending_name` in the expiring OTP challenge. The users collection is **not** modified by an OTP request or failed verification. After successful one-time challenge consumption, a farmer's `profile.name` is updated with `profile.name_source="self_reported"`; the response session and `/me` include it. Arbitrary name fields injected into `/auth/otp/verify` cannot replace the challenge-bound name. No-name legacy requests preserve an existing name, and expert fixture names are not overwritten. Audit records record the update event/source without duplicating the name. Existing profile attributes are retained.

The full name appears in Overview and the account menu; current user data is refreshed from `/me` and cached for offline reload. English, Hindi, and Punjabi labels and names are supported. OTP transport remains the explicitly labeled demo; correct demo code is not real-world proof of phone ownership.

### Camera behavior

- Crop-photo and Soil Health Card attachment modes have a **Take photo** button in addition to gallery/file upload.
- Its dedicated input is `type="file" accept="image/*" capture="environment"`, with no `multiple`; only a direct click invokes the chooser. The gallery input remains separate and has no capture attribute.
- Supported mobile browsers hand off to native camera selection, preferring the rear camera. Desktop browsers may show a file chooser. The application does not request continuous camera access, track video, or claim a particular native camera UI.
- Returning a supported photo produces a preview, filename and ready message. Cancellation does not clear existing attachments. Removal and same-file recapture are supported.
- Existing JPEG/PNG/WebP size/type validation, compression, five-file limit, authenticated upload, deduplication and offline queue apply. Unsupported camera formats such as HEIC receive a clear supported-format message; no unsupported decoding is claimed.
- Submission is disabled while attachment preparation or audio recording is active, avoiding missing-file submissions.

### Verification

`test_reports/iteration_2.json`: seven focused backend tests and twelve existing backend tests passed. Focused source: `backend/app/tests/test_identity_camera_regression.py`. UI checks covered full-name login, OTP-stage fields, name persistence/reload, long and Punjabi names, dedicated capture-input attributes, chooser invocation/cancellation/reselection, preview and uploaded-ID linkage into advisories. Desktop 1920×800/mobile 390×844 checks found no horizontal overflow. `yarn tsc --noEmit` and optimized production build passed; log `test_reports/name-camera-build.log`.

Headless testing exercised the browser capture/file-chooser contract and photo-upload path, not a physical phone's external camera application. Real Aadhaar, SMS, Google Maps and OpenWeather have not been enabled or tested.