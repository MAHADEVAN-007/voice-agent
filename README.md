# VocalKart — AI Voice Ordering Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)]()
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)]()
[![LiveKit](https://img.shields.io/badge/LiveKit-Cloud-00E5FF?logo=livekit)]()
[![License](https://img.shields.io/badge/License-Proprietary-red)]()

AI-powered wholesale ordering for kirana stores. Customers enter their phone, get admin approval, verify via OTP, and receive an AI voice call (Hindi/English) that takes their order. WhatsApp confirmation sent automatically.

🔗 **Live:** https://vocal-kart-voice-agent.onrender.com

---

## Flow

1. User enters phone → admin gets email approval link
2. Admin approves from panel → user sees "Access Approved!"
3. User requests OTP → enters 6-char code → verified
4. User clicks "Call Agent" → AI voice call takes order
5. WhatsApp sends order summary

---

## Tech Stack

**Backend:** Python, FastAPI, Uvicorn, LiveKit Agents, Twilio, Resend
**Frontend:** React 19, TypeScript, Vite, Tailwind CSS 4, Motion, Radix UI
**Infra:** LiveKit Cloud (SIP + agent), Render, Supabase (PostgreSQL), Cloudflare Turnstile

---

## Quick Start

```bash
git clone <repo>
cd voice-agent

# Backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

Set env vars (see `.env`), then:

```bash
# Terminal 1
python -m uvicorn token_server:app --host 0.0.0.0 --port 8080 --reload

# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | ✅ | LiveKit Cloud WSS URL |
| `LIVEKIT_API_KEY` | ✅ | LiveKit API key |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit API secret |
| `LIVEKIT_OUTBOUND_TRUNK_ID` | ✅ | SIP trunk ID |
| `ADMIN_SECRET` | ✅ | Admin panel password |
| `TWILIO_ACCOUNT_SID` | For SMS | Twilio SID |
| `TWILIO_AUTH_TOKEN` | For SMS | Twilio auth token |
| `TWILIO_MOBILE_NUMBER` | For SMS | Twilio SMS number |
| `RESEND_API_KEY` | For email | Resend API key |
| `TURNSTILE_SECRET_KEY` | For bot protection | Cloudflare secret |

Frontend `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_TURNSTILE_SITE_KEY` | For bot protection | Turnstile site key |

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/request-access` | Request admin approval |
| `GET` | `/api/request-status/{id}` | Poll approval status |
| `POST` | `/api/send-otp` | Send OTP via SMS |
| `POST` | `/api/verify-otp` | Verify OTP |
| `POST` | `/api/create-session` | Initiate voice call |
| `GET` | `/api/admin/list-requests` | List requests (admin) |
| `POST` | `/api/admin/respond-request` | Approve/reject (admin) |
| `GET` | `/api/health` | Health check |

---

## Admin Panel

```
/admin?secret=YOUR_ADMIN_SECRET
```

Lists pending requests. Approve or reject with one click. Auto-refreshes every 5s.

---

## Deployment (Render)

**Build:**
```bash
cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt
```

**Start:**
```bash
uvicorn token_server:app --host 0.0.0.0 --port 8080
```

Set all env vars in Render Dashboard. `VITE_TURNSTILE_SITE_KEY` must be **build-time**.

---

## Project Structure

```
voice-agent/
├── token_server.py     # FastAPI entry point
├── admin.py            # Admin panel
├── email_service.py    # Resend emails
├── otp.py              # Twilio OTP
├── call.py             # LiveKit SIP calls
├── agent.py            # AI voice agent
├── database.py         # DB models
├── whatsapp.py         # WhatsApp messages
├── requirements.txt    # Python deps
├── .env                # Env vars
└── frontend/           # React app
```

---

## Rate Limiting

- **2 calls / phone / 24h**
- **5 calls / IP / 1h**

---

## License

Proprietary — All rights reserved.
