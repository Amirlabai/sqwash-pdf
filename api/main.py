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

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )


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
