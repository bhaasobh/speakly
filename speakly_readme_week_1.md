# Speakly
**From voice to clear notes — English • Hebrew • Arabic**

This repo contains:
- **mobile/** – Expo React Native app (record, save `.m4a`, upload)
- **speakly-server/** – FastAPI backend (`/session/create`, `/upload`, `/health`)

> **Week 1 scope (done):**
> - Record audio on device (Expo `expo-av`)
> - Save locally as `.m4a`
> - Create a server session
> - Upload clip(s) to `uploads/<session_id>/clip_*.m4a`
> - Robust client networking (timeouts, retries, alerts)

---

## 1) Repo Structure
```
Speakly/
├── mobile/                      # Expo app
│   ├── App.js
│   └── src/
│       ├── config/server.js     # resolves SERVER base URL (sim/emulator/device/.env)
│       └── lib/net.js           # fetchJSON() + uploadFile() with retries/timeouts
└── speakly-server/              # FastAPI backend
    └── main.py
```

---

## 2) Prerequisites
- **Node 18+** and **npm** (or yarn/pnpm)
- **Expo CLI** (`npm i -g expo-cli`) – optional, `npx expo` works too
- **Python 3.10+**
- **ffmpeg** (optional, for generating/inspecting audio)

---

## 3) Backend – FastAPI

### Install & run
```bash
cd speakly-server
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install fastapi uvicorn[standard] python-multipart pydantic[dotenv]
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
You should see: `Uvicorn running on http://0.0.0.0:8000`.

### Endpoints
- `GET /health` → `{ "ok": true }`
- `POST /session/create` → `{ session_id, title }` (accepts JSON `{title}` or form `title`)
- `POST /upload` (multipart/form-data) → `{ ok, saved, size }`

> **Uploads path:** `speakly-server/uploads/<session_id>/clip_*.m4a`

**Windows firewall tip:** Allow inbound TCP:8000 or run:
```powershell
netsh advfirewall firewall add rule name="Uvicorn 8000" dir=in action=allow protocol=TCP localport=8000
```

---

## 4) Mobile – Expo React Native

### Install & run
```bash
cd mobile
npm install
npx expo start -c
```
Open on:
- **iOS simulator:** press `i`
- **Android emulator:** press `a`
- **Physical device:** scan QR in Expo Go

### Configure server URL
`mobile/src/config/server.js` decides the base URL:
- iOS simulator → `http://127.0.0.1:8000`
- Android emulator → `http://10.0.2.2:8000`
- Real device → **replace** with your PC LAN IP, e.g. `http://192.168.1.133:8000`

Optionally set via `.env` or `app.json`:
```env
# mobile/.env
EXPO_PUBLIC_SERVER_URL=http://192.168.1.133:8000
```
```json
// mobile/app.json
{
  "expo": {
    "extra": { "serverUrl": "http://192.168.1.133:8000" }
  }
}
```

> iOS: Allow **Local Network** for Expo Go.  Android: emulator can use `10.0.2.2`.

---

## 5) Day-by-Day (Week 1)
- **Day 1–2:** Record `.m4a` locally with `expo-av`; save to documents folder
- **Day 3:** Spin up FastAPI backend, `/session/create` + `/upload`
- **Day 4:** Wire app → server (session + file upload)
- **Day 5:** Robustness (timeouts, retries, alerts), server URL parameterized
- **Day 6:** UI polish; record a 30–60s clip; confirm upload

---

## 6) How to Run (quick)
1) **Server:**
```bash
cd speakly-server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
2) **App:**
```bash
cd mobile
npx expo start -c
```
3) In the app:
   - Tap **Create Session**
   - Tap **Start** → speak for 30–60s
   - Tap **Stop & Upload**  
   Expect: banner "Uploaded ✓" and file under `speakly-server/uploads/<session_id>/clip_0.m4a`

---

## 7) Screenshots
Create a folder `mobile/screenshots/` and drop images, then reference:

```
mobile/screenshots/
  01-home.png
  02-recording.png
  03-uploaded.png
```

Markdown (README view on GitHub):
```md
![Home](mobile/screenshots/01-home.png)
![Recording](mobile/screenshots/02-recording.png)
![Uploaded](mobile/screenshots/03-uploaded.png)
```

Tips:
- Use Expo’s screenshot (simulator) or device screenshots
- Keep sizes under ~1MB each

---

## 8) Troubleshooting
- **Network request failed:**
  - Run server with `--host 0.0.0.0` and use LAN IP in app
  - Ensure same Wi‑Fi; disable VPN; allow local network on iOS
  - Windows firewall rule for TCP:8000
- **422 on /upload:**
  - Use multipart/form-data; in Postman set `file` field type to **File**
- **invalid session_id:**
  - Create session after server restart; or auto-create dir (code already does)
- **Expo not refreshing:** enable **Fast Refresh**; `npx expo start -c` for cache

---

## 9) Roadmap (Week 2+)
- **Week 2:** STT service (faster‑whisper) + live captions via WebSocket
- **Week 3:** Multilingual summarization (mT5/mBART) → bullets/actions/decisions
- **Week 4:** Speaker diarization (optional), exports (PDF/Markdown)

---

## 10) License
MIT (or your choice)

