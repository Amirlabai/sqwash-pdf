# sqwash-pdf

## Purpose

Flatten PDF files by rasterizing each page to JPEG and rebuilding a new PDF. This removes editable layers and can reduce file size.

## Architecture

- `lib/flatten.py` — shared in-memory flatten logic (`flatten_pdf_bytes`)
- `flatten_pdf.py` — desktop CLI with Tkinter file picker
- `api/main.py` — FastAPI service for browser uploads
- `web/` — static frontend deployed on Vercel

Production hosting split:

- Vercel: static UI at https://sqwash-pdf.vercel.app
- Render: FastAPI API at https://sqwash-pdf.onrender.com
- Browser uploads call Render directly (avoids Vercel proxy body limits)

Local development:

```powershell
Set-Location "C:\Users\amirl\OneDrive\Documents\GitHub\sqwash-pdf"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Open `http://localhost:8000` for UI and API together.

## Key parameters

- DPI: 72–300 (default 150)
- JPEG quality: 0–100 (default 75)
- Upload limit: 25 MB per PDF

## Environment variables

### Vercel (`web/`)

- `API_URL` — Render service origin, no trailing slash: `https://sqwash-pdf.onrender.com`. Baked into `config.js` at build time.
- Build command: `npm run build`
- Output directory: `.` (set in generated `vercel.json`)
- Root directory: `web`

### Render

- `VERCEL_APP_URL` — production Vercel origin, no trailing slash: `https://sqwash-pdf.vercel.app`
- `ALLOWED_ORIGINS` — extra comma-separated origins (example: `http://localhost:8000` for local UI against Render API)
- `ALLOW_VERCEL_PREVIEWS` — `true` (default) allows all `https://*.vercel.app` preview deploys
- `PORT` — set automatically on Render

Example Render env:

```
VERCEL_APP_URL=https://sqwash-pdf.vercel.app
ALLOWED_ORIGINS=http://localhost:8000
ALLOW_VERCEL_PREVIEWS=true
```

Example Vercel env:

```
API_URL=https://sqwash-pdf.onrender.com
```

## Deployment notes

- `VERCEL_APP_URL` on Render must match the live Vercel app (`https://sqwash-pdf.vercel.app`).
- `API_URL` on Vercel must match the live Render service (`https://sqwash-pdf.onrender.com`).
- Render free tier sleeps after 15 minutes idle; first request may take ~30–60 seconds.
