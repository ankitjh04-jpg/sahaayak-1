# Sahaayak — Product Requirements & Handoff

## Original problem statement

Build a clean, build-ready SIH26131 repository implementing **Detect → Predict → Advise → Validate → Monitor**. Frontend React + TypeScript responsive; backend modular FastAPI; MongoDB. Farmer and agricultural expert roles; phone OTP through an adapter; Punjabi/Hindi/English. Visual direction: deep green sidebar, cream canvas, dark serif headings, rounded cards, gold accents, generous spacing, mobile bottom navigation.

Farmer signs in, creates field (crop/location/acreage/sowing date/optional soil), submits text/voice/image/Soil Health Card, receives validated structured cited guidance. Missing data must produce clearly labeled general guidance, not a fabricated result. Listen and WhatsApp summary flows; low-confidence expert queue; expert validation/edits/rationale/source audited. Verified records enter monitoring, never automatic model training.

Required API prefix `/api/v1`: OTP request/verify, me, fields create/list, advisories create/list/detail/feedback, expert cases/review, uploads, health. Resource-heavy jobs return job ID/status. Collections users, fields, advisories, expert_reviews, uploads, knowledge_sources, jobs; add security/audit collections as needed.

All integrations behind adapters: OpenAI Whisper/structured multilingual response/optional speech; vision fixtures then CNN/YOLO; deterministic risk then RF/XGBoost; cited verified RAG; weather live/cached/no-data; Leaflet/OSM; OTP; Twilio WhatsApp with retries; private object storage (Mongo metadata only). No exposed keys; owner must revoke previously exposed OpenAI key privately. Env-only credentials, gitignore env except examples, RBAC/owner/case checks, OTP expiry/attempt/rate limiting, upload size/type/checksum, audit, client compression, offline queue/reconnect, explicit uncertainty and provider failures. Include tests, Docker, README and comprehensive `docs/SAHAAYAK_TECHNICAL_DOCUMENT.md` with setup/architecture/API/indexes/flows/replacement/safety/testing/release instructions.

## Explicit user choices

- Credential-free SIH demo with clearly labeled simulated OTP, vision, voice, WhatsApp.
- No screenshot supplied; follow written design direction.
- English first, Hindi and Punjabi available.
- Follow-up (2026-09-09): authorized Aadhaar verification desired, but actual provider name/docs absent; Twilio selected for SMS OTP; Google Maps + OpenWeather selected; native camera launch selected. Final user choice explicitly limits current implementation to farmer-name and camera changes while credentials are pending.

## Personas

- Farmer: mobile-first, limited bandwidth, seasonal crop questions, clear trustworthy guidance in preferred language.
- Agricultural expert: review uncertain cases, inspect original inputs/sources, document traceable decisions.
- SIH evaluator: reproducible credential-free end-to-end workflow and honest model/provider boundaries.

## Architecture decisions

- `/app` is requested repository root (not duplicated under nested sahaayak/).
- React 19 + TypeScript within existing CRA/Craco runner; shadcn/Radix buttons/dialog; React Router; Leaflet; Sonner. Lora + DM Sans + Noto language fonts.
- Compatibility `src/App.js` imports `main.tsx`; original jsconfig removed to avoid TypeScript conflict.
- FastAPI `app.main:app`; `server.py` compatibility entry; Motor uses protected MONGO_URL/DB_NAME. UUID string IDs, projections exclude BSON IDs.
- Mongo-persisted opaque expiring sessions; demo auth endpoints deliberately public only in DEMO_MODE. Live auth not claimed.
- Background Mongo jobs with atomic claim, restart repair, bounded retry; one demo worker.
- Deterministic curated FAO general IPM retrieval, not vector RAG. Null diagnosis/risk/confidence; all new cases escalated.
- Real private local filesystem storage behind adapter, metadata/dedup in Mongo; not a cloud bucket.
- IndexedDB per-owner queue contains files and stable idempotency key; static-shell SW, no API/OSM caching.
- External API origin exclusively frontend env. No live credentials required or introduced.

## Implemented — 2026-09-08

- Responsive seeded farmer dashboard, field grid/detail/form/map, advisory compose/result/history, expert queue/review/monitoring export, source library, login and mobile navigation.
- Real field/advisory/review/feedback/upload/job persistence; OTP simulation with expiry, attempt limits/replay checks/rate limiting; role/owner checks; validated private uploads and deduplication.
- Cited general multilingual responses, missing inputs, assumptions, null diagnostic score, audited expert decisions, no auto-training.
- Image compression; crop/PDF/audio upload; browser audio recording permission handling and duration cap; browser read-aloud when installed voices exist.
- Simulated WhatsApp queued retries then explicit not sent; provider no-data fallbacks; no invented disease/forecast/transcript.
- Offline text/file queue persists through reload; reconnect sync; failed item retry/removal; persistent per-owner sync confirmation; immediate history refresh.
- README, backend/frontend/root env examples, Dockerfiles/Compose/nginx, detailed technical documentation, pytest suite and screenshots.
- Removed unrelated starter analytics and updated document metadata.

## Verification — 2026-09-08

- Testing agent report `test_reports/iteration_1.json`: backend 12/12, core UI flow passes, initial frontend 82% with two minor followups.
- `yarn tsc --noEmit` and `yarn build` passed (testing agent logs in test_reports).
- Followups fixed/reproduced: native option hydration warning removed, offline auto-sync race made explicit and confirmed with file+reload/reconnect, expired OTP HTTP400, microphone NotAllowedError graceful feedback.
- Desktop 1920×800/mobile390×844 screenshots; core screens no horizontal overflow. Sonner mobile container fix verified in final pass.
- Seeded demo records are separate from test artifacts. No live provider integration was tested/claimed. Docker configuration provided; Docker engine execution not verified in this environment.
- Final follow-up summary: `test_reports/final_status.json`. Final optimized frontend build and tsc pass; mobile notification overflow resolved; clean dashboard restored to 2 fields and 3 advisories. No unresolved failures in exercised demo flows.

## Static safety requirements

## Follow-up implementation — 2026-09-09

User request: "in the user login page add adhaaar card credentials of farmers(with verification giving otp in my phone number after pressing verify button),as well as the name of the farmer so that it reflects onto the main page(overview page), add google maps api(to track the location of the farmer),weather api as per the location map, and also add camera option in the mobile app(in the new advisroy section) so when we click on the option it will open the camera app".

Agreed delivered scope: required farmer full name on login, challenge-bound name persistence after successful demo OTP, full name on Overview/account menu, and native Take photo alongside gallery. Backend API name is optional for legacy clients; Unicode validation and normalization apply. Failed/request-only OTP cannot mutate the profile; verify-payload name cannot override the challenge; expert fixture names protected. Names explicitly self-reported, not Aadhaar-verified.

Camera uses a separate single-file `accept=image/* capture=environment` input. Preview, cancellation, removal/reselection, file validation, compression, real uploads and offline submission remain connected. Browser/OS decides native camera vs file picker; physical external camera app was not tested by headless browser. Submit disabled during preparation/recording.

Verification: testing agent `test_reports/iteration_2.json`, focused 7/7 and prior 12/12 backend tests; desktop/mobile UI flows with no overflow. Current tsc and production build pass. Report has no scoped bugs; optional future expiry-clock/toast assertion coverage remains. Only test code/report changed by testing agent; reviewed by main agent. Existing user field records must not be broadly deleted: user has begun entering their own data.

Pending explicitly: authorized Aadhaar provider's exact identity/docs/account authorization; private Twilio, Google Maps, OpenWeather credentials. No Aadhaar number field/data storage, no actual SMS, no Google Maps/OpenWeather integration added. Existing OSM and no-weather-data behavior intentionally retained. Do not claim these integrations live.

## Static safety requirements (continued)

Never invent diagnosis, probability, weather, yield, dosage, or transcript. Never treat general-source validation as confirmed field diagnosis. Never auto-train from verified records. Never expose credentials or raw provider exceptions. Missing/uncertain inputs must stay visible. Real-world expert provisioning and phone verification require live provider implementation and separate governance.

## Prioritized backlog / next tasks

### P0 before real farmer use (not required for credential-free demo)
- Owner revokes any previously exposed key; no revocation was performed by app.
- Implement live OTP provider, trusted expert provisioning; disable public demo endpoints.
- Provider-specific integration/timeout/signature tests, encryption/retention/consent, malware quarantine.
- Approved regional crop knowledge and expert-reviewed full Hindi/Punjabi operational-copy translation.

### P1
- Calibrated vision + quality abstention; live weather with stale cache rules; validated risk model; Whisper/structured response adapters.
- Private S3-compatible store and Twilio real delivery/callbacks.
- Multi-process leases/outbox/transactions, finer-grained expert assignment, audit retention.
- Full accessibility/font sizing/contrast review and device voice availability QA.

### P2
- Consented expert-verified regional crop alerts/hotspot visualization (none inferred currently).
- Scheduled field follow-ups and progress comparisons.
- Approved evaluation dataset governance; any model training remains separate/opt-in.

## Next product suggestion

Field follow-up reminders would help farmers revisit symptoms and experts monitor whether a verified recommendation helped.