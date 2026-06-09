# sqwash-pdf

## Purpose

Flatten PDF files by rasterizing each page to JPEG and rebuilding a new PDF. This removes editable layers and can reduce file size.

## Architecture

- `lib/flatten.py` — shared in-memory flatten logic (`flatten_pdf_bytes`)
- `flatten_pdf.py` — desktop CLI with Tkinter file picker
- `api/main.py` — FastAPI service for browser uploads
- `web/` — static frontend deployed on Vercel

Production hosting split:

- Vercel: static UI in `web/`, proxies `/api/*` to Render
- Render: FastAPI API (`uvicorn api.main:app`)

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

- `ALLOWED_ORIGINS` — comma-separated CORS origins for direct API access (optional when using Vercel rewrites)
- `PORT` — set automatically on Render

## Deployment notes

- Update `web/vercel.json` rewrite destination to your Render service URL after first deploy.
- Render free tier sleeps after 15 minutes idle; first request may take ~30–60 seconds.
