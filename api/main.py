import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from lib.flatten import (
    EmptyPdfError,
    FlattenError,
    InvalidPdfError,
    flatten_pdf_bytes,
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="sqwash-pdf API")

def _parse_allowed_origins() -> list[str]:
    origins = [
        origin.strip().rstrip("/")
        for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]

    vercel_app_url = os.environ.get("VERCEL_APP_URL", "").strip().rstrip("/")
    if vercel_app_url and vercel_app_url not in origins:
        origins.append(vercel_app_url)

    return origins


def _allow_vercel_previews() -> bool:
    return os.environ.get("ALLOW_VERCEL_PREVIEWS", "true").lower() in ("1", "true", "yes")


allowed_origins = _parse_allowed_origins()
allow_vercel_previews = _allow_vercel_previews()

if allowed_origins or allow_vercel_previews:
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["*"],
    }
    if allowed_origins:
        cors_kwargs["allow_origins"] = allowed_origins
    if allow_vercel_previews:
        cors_kwargs["allow_origin_regex"] = r"https://.*\.vercel\.app"

    app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/flatten")
async def flatten_pdf_endpoint(
    file: UploadFile = File(...),
    dpi: int = Form(150),
    jpg_quality: int = Form(75),
):
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(pdf_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.",
        )

    try:
        output_bytes = flatten_pdf_bytes(pdf_bytes, dpi=dpi, jpg_quality=jpg_quality)
    except (InvalidPdfError, EmptyPdfError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FlattenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to flatten PDF.") from exc

    stem = Path(filename).stem
    output_filename = f"{stem}-flat-{dpi}.pdf"

    return Response(
        content=output_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
    )


if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
