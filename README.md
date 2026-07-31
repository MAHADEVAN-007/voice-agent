# VocalKart — AI Voice Ordering for Kirana Stores

VocalKart is a voice-first wholesale ordering platform for kirana (grocery) stores. Store owners dial in, speak their order in **Hindi or English**, and an AI agent named **Raj** takes it live over the phone — complete with real inventory, MRP and case pricing, and running schemes. The final order is sent as a **WhatsApp summary** for confirmation.

> Live demo: [https://vocal-kart-voice-agent.onrender.com](https://vocal-kart-voice-agent.onrender.com)

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **Bilingual voice ordering** — the AI agent understands and replies in Hindi and English.
- **Real inventory & schemes** — every product lookup is validated against the live database (product, MRP, price per case, running schemes like *buy 2 get 3 free*).
- **LiveKit real-time voice** — low-latency agent with VAD (Silero) and Sarvam AI speech-to-text / text-to-speech.
- **Granular LLM control** — the agent is a small, focused model (Gemma 4 31B via Groq) with function/tool calling and a low token budget so it never rambles.
- **Admin approval flow** — new store owners must be approved by the admin via a secure, one-time email link before they can place calls.
- **WhatsApp order summary** — after each call, a structured order summary is delivered to the store owner's WhatsApp.
- **Cloudflare Turnstile** — bot protection on the public form (with a working OTP resend flow).

---

## How It Works

```
┌────────────┐  phone + OTP   ┌───────────────────┐
│ Store owner│──────────────▶│  Landing page      │
└────────────┘                │  (Turnstile + OTP)│
                              └─────────┬─────────┘
                                        │ create access request
                                        ▼
                    ┌───────────────────────────────┐
                    │  Admin receives email with    │
                    │  one-time /admin?request_id=  │
                    └───────────────┬───────────────┘
                                    │ approve / reject
                                    ▼
                    ┌───────────────────────────────┐
                    │  Owner verifies OTP, opens    │
                    │  the LiveKit call room        │
                    └───────────────┬───────────────┘
                                    ▼
        ┌───────────────────────────────────────────────┐
        │  LiveKit Cloud + SIP outbound/inbound call    │
        │  → AI agent "Raj" (Gemma 4 31B)               │
        │  → catalog_lookup tool queries inventory      │
        └───────────────────────┬───────────────────────┘
                                │ order captured
                                ▼
                    ┌───────────────────────────────┐
                    │  WhatsApp order summary sent  │
                    │  to the store owner           │
                    └───────────────────────────────┘
```

---

## Tech Stack

| Layer       | Technology |
|-------------|-----------|
| Backend     | Python 3.12+, FastAPI, SQLAlchemy (async) |
| Voice agent | LiveKit Agents (v1.6), Silero VAD, Sarvam AI (STT/TTS), Google **Gemma 4 31B** via Groq |
| Frontend    | React 19, TypeScript, Vite 6, Tailwind CSS 4, LiveKit Components, Cloudflare Turnstile |
| Database    | PostgreSQL (Supabase) |
| Telephony   | Twilio (SMS OTP + inbound TwiML), LiveKit SIP (VoBiz trunk) |
| WhatsApp    | Twilio WhatsApp + Whatomate fallback |
| Email       | Resend |
| Hosting     | Render (backend + frontend), LiveKit Cloud |

---

## Getting Started

### Prerequisites

- Python **3.12+** with [uv](https://docs.astral.sh/uv/) (or pip)
- Node.js **20+** and npm
- Accounts: LiveKit Cloud, Groq, Sarvam AI, Supabase/Postgres, Twilio, Cloudflare (Turnstile), Resend, VoBiz SIP

### 1. Backend setup

```bash
uv sync
```

Create a `.env` file at the project root — see [Environment Variables](#environment-variables).

### 2. Database

```bash
uv run init_db.py
```

This creates the tables and seeds the inventory with the built-in kirana product catalog (Coca-Cola, Sprite, Maggi, Parle-G, Amul, Lays, etc.).

### 3. Run the backend

```bash
uv run uvicorn token_server:app --port 8080 --reload
```

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### 5. Place a test call

```bash
uv run call.py +91XXXXXXXXXX
```

`call.py` creates a LiveKit SIP outbound trunk (saved to `LIVEKIT_OUTBOUND_TRUNK_ID`) and dispatches the agent into the call.

---

## Environment Variables

All values live in `.env` (not committed). `VITE_*` variables are also required in the Render dashboard for the frontend build.

| Variable | Description |
|----------|-------------|
| `LIVEKIT_URL` | LiveKit Cloud WebSocket URL |
| `LIVEKIT_API_KEY` | LiveKit Cloud API key |
| `LIVEKIT_API_SECRET` | LiveKit Cloud API secret |
| `LIVEKIT_SIP_ENDPOINT` | LiveKit SIP endpoint |
| `LIVEKIT_INBOUND_NNUMBER` | Inbound SIP number |
| `LIVEKIT_OUTBOUND_TRUNK_ID` | SIP outbound trunk ID (auto-created by `call.py`) |
| `SARVAM_API_KEY` | Sarvam AI key (STT/TTS) |
| `GROQ_API_KEY` | Groq key (Gemma 4 31B LLM) |
| `DATABASE_URL` | SQLAlchemy async Postgres URL (Supabase) |
| `SUPABASE_URL` / `SUPABASE_KEY` | Supabase project credentials |
| `TURNSTILE_SITE_KEY` / `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile widget + verify secret |
| `VITE_TURNSTILE_SITE_KEY` | Turnstile site key for the frontend build (Render) |
| `VOBIZ_SIP_DOMAIN` | VoBiz SIP trunk domain |
| `VOBIZ_USERNAME` / `VOBIZ_PASSWORD` | VoBiz SIP credentials |
| `VOBIZ_OUTBOUND_NUMBER` | Outbound caller ID number |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Twilio credentials (SMS OTP + WhatsApp) |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp sender number |
| `TWILIO_INBOUND_TWIML` | Inbound TwiML webhook URL for calls |
| `WHATOMATE_WHATSAPP_API_KEY` | Whatomate WhatsApp API key (fallback sender) |
| `ADMIN_EMAIL` | Email address that receives approval requests |
| `RESEND_API_KEY` / `RESEND_FROM_EMAIL` | Resend email credentials |
| `PUBLIC_URL` | Public base URL (e.g. `https://vocal-kart-voice-agent.onrender.com`) |

---

## Admin Panel

When a store owner requests access, the admin receives an email with a link:

```
https://<host>/admin?request_id=<uuid>
```

The link is single-use: it only works while the request is still **pending**, so it doubles as the auth token — no shared admin password needed. Approve or reject the request from there; approved users then get their OTP to start placing calls.

---

## Deploying on Render

- **Backend** — start command: `uv run uvicorn token_server:app --host 0.0.0.0 --port $PORT` (or `uvicorn` + gunicorn worker). Set every non-`VITE_` variable from the table above.
- **Frontend** — build command `npm run build` (in `frontend/`) and output `dist`. Set `VITE_TURNSTILE_SITE_KEY` for the build, or the Turnstile widget won't render.
- LiveKit agent should be deployed so it can be dispatched into calls (see `call.py` → `agent_dispatch`).

---

## Troubleshooting

- **`503 Service unavailable` on sending OTP** — Twilio **trial accounts can only message/call verified numbers**. Add the phone number under **Twilio Console → Verified Caller IDs**.
- **Turnstile won't render on Render** — the frontend build needs `VITE_TURNSTILE_SITE_KEY` set in the Render environment at build time.
- **Admin link says `401 Unauthorized`** — the request was already approved, rejected, or expired. Ask the owner to submit a new request.
- **"Cannot resend OTP"** — resend is only offered after a valid phone number passes Turnstile; the button is intentionally disabled until then.

---

## Project Structure

```
.
├── agent.py            # LiveKit voice agent (STT/VAD/TTS + Gemma LLM + tools)
├── token_server.py     # FastAPI app: OTP, access requests, admin, tokens
├── admin.py            # Admin panel + approval endpoints
├── email_service.py    # Resend emails (admin approval links, OTP)
├── whatsapp.py         # WhatsApp order summary delivery
├── call.py             # LiveKit SIP outbound call + agent dispatch
├── otp.py              # OTP generation / verification
├── crud.py             # Database operations
├── models.py           # SQLAlchemy models (Inventory, AccessRequest)
├── database.py         # Async engine + session helpers
├── init_db.py          # Create tables + seed kirana inventory
├── prompt.py           # System prompt for the agent
├── requirements.txt    # Python dependencies (livekit-agents ~= 1.6)
└── frontend/
    ├── src/pages/      # LandingPage, CallPage
    ├── src/components/ # UI components
    └── src/hooks/      # LiveKit / call hooks
```

---

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2026
