import os
import re
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
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
RATE_LIMIT_PER_MINUTE = max(1, int(os.environ.get("RATE_LIMIT_PER_MINUTE", "10")))
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
_rate_limit_buckets: dict[str, list[float]] = defaultdict(list)

app = FastAPI(title="sqwash-pdf API")

def _parse_allowed_origins() -> list[str]:
    return [
        origin.strip().rstrip("/")
        for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _check_rate_limit(request: Request) -> None:
    client_ip = _client_ip(request)
    now = time.monotonic()
    recent_requests = [timestamp for timestamp in _rate_limit_buckets[client_ip] if now - timestamp < 60]
    if len(recent_requests) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many requests. Try again in a minute.")
    recent_requests.append(now)
    _rate_limit_buckets[client_ip] = recent_requests


allowed_origins = _parse_allowed_origins()

if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )


def attachment_content_disposition(filename: str) -> str:
    """Build a latin-1-safe Content-Disposition header for any Unicode filename."""
    encoded_filename = quote(filename)
    if filename.isascii():
        return f"attachment; filename=\"{filename}\""

    ascii_fallback_match = re.search(r"-flat-(\d+)\.pdf$", filename, re.IGNORECASE)
    ascii_fallback = (
        f"flat-{ascii_fallback_match.group(1)}.pdf"
        if ascii_fallback_match
        else "download.pdf"
    )
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_filename}"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/flatten")
async def flatten_pdf_endpoint(
    request: Request,
    file: UploadFile = File(...),
    dpi: int = Form(150),
    jpg_quality: int = Form(75),
):
    _check_rate_limit(request)

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
        headers={"Content-Disposition": attachment_content_disposition(output_filename)},
    )


if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
