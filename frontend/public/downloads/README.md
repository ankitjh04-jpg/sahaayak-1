# Sahaayak — Farmer & Agricultural Expert Workspace

**Detect → Predict → Advise → Validate → Monitor** · SIH26131 · v1.2

React + TypeScript frontend, FastAPI backend, MongoDB, farmer OTP login, protected expert login, mobile camera uploads, cited general advisories, review notifications, location maps, and live weather.

## What works, and what needs your credentials

| Feature | Current behavior |
|---|---|
| Farmer name | Saved after successful OTP verification; full name displayed on Overview |
| Twilio Verify SMS | Adapter implemented; automatically activates when all three Twilio credentials are configured. Without them, real SMS login is unavailable—never falsely successful |
| Farmer demo | Explicit **Farmer demo** button when `DEMO_MODE=true`; not real phone verification |
| Expert access | Email + password only, created by a local administrator. No public signup or demo bypass |
| Aadhaar | **Demo check only**. Returns `verified=false`; collects no Aadhaar number. Not proof of identity |
| Live weather | Open-Meteo without a key for noncommercial demo use; automatically uses OpenWeather when its key is configured |
| Google Maps | Activates with a restricted Google Maps browser key; otherwise an explicitly labeled OpenStreetMap fallback |
| Location | Explicit permission or a selected farm/map pin; no background tracking |
| Review notifications | Persistent farmer inbox + unread badge, refreshed every 15 seconds while app is visible; no OS push/email/SMS notification claimed |
| Camera | **Take photo** alongside gallery; native rear-camera capture request on supported phones, preview/remove/upload/offline queue |
| Advisory AI | Curated, cited general guidance. No automated disease diagnosis, fabricated confidence, pesticide dosage, or yield guarantee |
| WhatsApp | Existing simulated delivery flow only; not activated by Twilio Verify credentials |

**No real provider credentials are included.** Accounts and API keys cannot be created automatically on your behalf. Do not paste secrets into chat or Git.

## 1. Run directly from VS Code

### Prerequisites (install once)

- Python **3.11 or 3.12**
- Node.js **20 or 22**
- Yarn **1.22** (with Node 20/22: `corepack enable` then `corepack prepare yarn@1.22.22 --activate`)
- MongoDB Community Server running locally, or a MongoDB connection URI you control
- Internet for installing dependencies, weather, map tiles, and web fonts

Extract `sahaayak-local.zip`, open the extracted **sahaayak** folder in VS Code, and open its terminal. Run from the project root:

```bash
python scripts/setup_local.py
```

This creates `.venv`, installs the backend and frontend dependencies, and copies `.env.example` files **only if their `.env` files do not already exist**. It never replaces existing private settings. On systems where Python is `python3`, use that instead of `python`.

### Start MongoDB

Use your installed MongoDB service. Alternatively, for the Python/Node workflow with Docker only for Mongo, start a local bound Mongo container:

```bash
docker run -d --name sahaayak-mongo -p 127.0.0.1:27017:27017 -v sahaayak-local-mongo:/data/db mongo:7
```

Choose **one** database option. The default local backend URI is `mongodb://127.0.0.1:27017`.

### Configure an expert account

With MongoDB running:

```bash
python scripts/create_expert.py
```

Enter an email, full name, and a password of at least **12 characters**. Password input is hidden. There is no default expert password and no public expert registration.

To reset an existing expert password (also revokes their sessions):

```bash
python scripts/create_expert.py --email expert@example.com --reset-password
```

### Run frontend and backend together

```bash
python scripts/run_local.py
```

Open **http://localhost:3000**. Press **Ctrl+C** to stop both services.

- Farmer login: http://localhost:3000/login
- Expert login: http://localhost:3000/expert/login
- Backend API docs: http://localhost:8001/docs
- Health: http://localhost:8001/api/v1/health

### Separate VS Code terminals (optional)

After setup, in Terminal 1:

```bash
cd backend
# Windows:
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
# macOS/Linux (use this instead):
../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

In Terminal 2:

```bash
cd frontend
yarn start
```

Do not start both the combined runner and separate terminals at the same time.

## 2. Connect real farmer OTPs with Twilio

1. In your Twilio Console create **Verify → Services → Create Service**, name it Sahaayak, enable SMS, and set **6-digit codes**.
2. Obtain your Account SID (`AC…`), Auth Token, and Verify Service SID (`VA…`).
3. Enable your destination country in **Verify Geo Permissions**. For India, allow `+91` destinations. Trial accounts must verify the recipient number first.
4. Add credentials privately to **backend/.env**:

```dotenv
OTP_PROVIDER=auto
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
```

5. Restart the backend, then use farmer login. A Verify service manages sending numbers; you do **not** need to buy a Twilio phone number for this flow.

`auto` uses live Twilio only when all credentials are present. Missing/bad credentials, provider errors, expired codes, rate limits, and wrong codes never become successful verification. Provider approval is required. Codes are not stored in MongoDB or logs. Local expiry is 5 minutes, with 5 checks and a 30-second resend cooldown. Names update only after a successful one-time verification.

For explicitly simulated, offline development OTP testing only, set `OTP_PROVIDER=demo` **and** `DEMO_MODE=true`; the UI clearly labels the demo code. Use `OTP_PROVIDER=twilio` or `auto` for real users. Disable `DEMO_MODE` before real-world use to remove the public farmer demo and Aadhaar-demo endpoint.

## 3. Weather and Google Maps

### Weather works without a key for the SIH demo

`WEATHER_PROVIDER=auto` uses Open-Meteo when `OPENWEATHER_API_KEY` is empty. Data is a current **weather-model estimate**, not a sensor reading or field diagnosis. Source/time/precipitation interval are displayed; cached or stale data are labeled. Free Open-Meteo access is for noncommercial use within its limits. Commercial use requires appropriate provider licensing.

To use OpenWeather, enable Current Weather Data on your provider account and set:

```dotenv
OPENWEATHER_API_KEY=your_private_key
WEATHER_PROVIDER=auto
```

No weather-provider key is returned to React. The backend uses a 10-minute cache, bounded timeouts, and explicit stale/no-data handling.

### Google Maps configuration

In Google Cloud, enable **Maps JavaScript API** with billing configured as required by Google, create a key, restrict it to that API and your allowed website referrers (for example `http://localhost:3000/*`), then set:

```dotenv
GOOGLE_MAPS_BROWSER_KEY=your_restricted_browser_key
GOOGLE_MAPS_MAP_ID=DEMO_MAP_ID
```

Use your own Google Map ID for production. A Maps browser key is **inherently visible to the browser**, not a backend secret. Referrer/API restrictions are essential. The app returns only that public key via `/api/v1/config`; Twilio and OpenWeather secrets are never returned. Missing or failed Google configuration leaves a clearly labeled OpenStreetMap fallback.

Use **Map & weather → Use my location** to request GPS permission, or select a saved field/map point. Coordinates are sent to the provider to display conditions. There is no background tracking and no inferred disease hotspot.

## 4. Docker Compose alternative

From a fresh extracted project:

```bash
python scripts/configure_local.py
# Edit backend/.env privately if enabling real providers.
docker compose up --build -d
docker compose exec backend python -m app.manage
```

The last command prompts for an approved expert account. Open http://localhost:3000. To stop:

```bash
docker compose down
```

MongoDB and private uploads are named volumes. Do not use `down -v` unless you intend to delete the stored data. Docker requires a functioning Docker Engine; the Python/Node workflow does not.

## 5. Try the full advisory and notification flow

1. Sign in as a farmer through Twilio, or explicitly open **Farmer demo**.
2. Add a field and submit a typed question, crop photo, recorded/uploaded audio or Soil Health Card.
3. The saved job returns cited **general guidance**, missing inputs and uncertainty, then enters expert review.
4. In another browser/incognito session, sign in at `/expert/login` using your administrator-created credentials.
5. Review a case, enter recommendation/rationale/source, and save the decision.
6. The farmer receives an unread notification within the visible-app polling interval. Clicking it opens the exact advisory, including crop/photo cases. Read status persists.

Notifications are **in-app**, not push notifications when the browser is closed. Original uploads remain private. Local private-file storage can be replaced with an object-store adapter later.

## 6. Mobile use

The same responsive app has mobile navigation, expert sign-in, weather, notifications, camera capture, and offline submission. It is a mobile web app, not a generated Android/iOS binary.

For another device on your LAN, set `frontend/.env` `REACT_APP_BACKEND_URL` to your computer's reachable backend address and set `backend/.env` `FRONTEND_ORIGIN` to the exact frontend address. Rebuild/restart after changing origins. Phone GPS and microphone generally require **HTTPS**; a desktop's localhost exception does not apply to a plain HTTP LAN address. The OS/browser decides whether the camera input opens its camera app or a file picker.

## 7. Security and test notes

- Aadhaar demo completion is never identity verification (`verified=false`). No Aadhaar number is collected, stored, or bypassed as genuine verification.
- Experts are provisioned locally, passwords PBKDF2-SHA256 hashed, sessions expire, and old/public expert demo sessions are rejected.
- Farmer owner/case authorization, rate limits, upload type/size/checksum validation and audit trails remain enforced.
- Verified advice becomes monitoring data, not automatic training data. No diagnosis, dosage or yield is guaranteed.
- Revoke any previously exposed provider keys yourself before adding replacements privately. The app cannot revoke keys in your external account.

Checks (using the created virtualenv):

```bash
# Windows:
.venv\Scripts\python.exe -m pip install -e "./backend[test]"
.venv\Scripts\python.exe -m pytest backend/app/tests -q
# macOS/Linux:
.venv/bin/python -m pip install -e "./backend[test]"
.venv/bin/python -m pytest backend/app/tests -q
# Frontend (both):
cd frontend
yarn tsc --noEmit
yarn build
```

Some provider tests use isolated HTTP fixtures; real Twilio SMS and Google Maps require your actual configured accounts. No claim of real delivery is made by fixture tests.

## Repository layout

```text
sahaayak/
  backend/app/          FastAPI APIs, schemas, services, integrations, security, tests
  backend/pyproject.toml  Minimal reproducible runtime dependencies
  frontend/src/        React TypeScript pages, UI, maps, notifications, camera
  frontend/public/     Static assets and offline shell
  scripts/             Local setup, expert provisioning, run and source packaging
  docs/SAHAAYAK_TECHNICAL_DOCUMENT.md
  docker-compose.yml
  .env.example         Public template only
```

The source download excludes `.env`, passwords, API keys, databases, uploaded farmer files, dependencies and generated build output. See the technical document for API contracts, indexes, adapter boundaries, and operational considerations.