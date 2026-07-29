# sqwash-pdf

## Purpose

Flatten PDF files by rasterizing each page to JPEG and rebuilding a new PDF. This removes editable layers and can reduce file size.

## Architecture

- `lib/flatten.py` — shared in-memory flatten logic (`flatten_pdf_bytes`)
- `flatten_pdf.py` — desktop CLI with Tkinter file picker
- `api/main.py` — FastAPI service (API + static UI)
- `web/` — static frontend served by FastAPI

Production hosting:

- Render: single web service at https://sqwash-pdf.onrender.com (UI and API, same origin)

Local development:

```powershell
Set-Location "<repo-root>"
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

### Render

- `ALLOWED_ORIGINS` — optional comma-separated origins for CORS (not needed for same-origin UI)
- `RATE_LIMIT_PER_MINUTE` — per-IP cap on `POST /api/flatten` (default `10`)
- `PORT` — set automatically on Render

Example Render env:

```
RATE_LIMIT_PER_MINUTE=10
```

## Deployment notes

- Deploy from repo root with `render.yaml` (service name `sqwash-pdf`).
- UI is served from `web/` by FastAPI; browser calls `/api/flatten` on the same host.
- Render free tier sleeps after 15 minutes idle; first request may take ~30–60 seconds.
