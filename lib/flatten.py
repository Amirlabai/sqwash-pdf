import fitz  # PyMuPDF

MIN_DPI = 72
MAX_DPI = 300
MIN_JPG_QUALITY = 0
MAX_JPG_QUALITY = 100


class FlattenError(Exception):
    """Base error for PDF flattening failures."""


class InvalidPdfError(FlattenError):
    """Raised when input bytes are not a valid PDF."""


class EmptyPdfError(FlattenError):
    """Raised when the PDF has no pages."""


def clamp_dpi(dpi: int) -> int:
    return max(MIN_DPI, min(MAX_DPI, dpi))


def clamp_jpg_quality(jpg_quality: int) -> int:
    return max(MIN_JPG_QUALITY, min(MAX_JPG_QUALITY, jpg_quality))


def flatten_pdf_bytes(
    pdf_bytes: bytes,
    *,
    dpi: int = 150,
    jpg_quality: int = 75,
) -> bytes:
    """Rasterize each page and rebuild a flat PDF; return output bytes."""
    dpi = clamp_dpi(dpi)
    jpg_quality = clamp_jpg_quality(jpg_quality)

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise InvalidPdfError("Input is not a valid PDF.") from exc

    try:
        if len(doc) == 0:
            raise EmptyPdfError("PDF has no pages.")

        output_doc = fitz.open()
        try:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                img_data = pix.tobytes("jpg", jpg_quality=jpg_quality)

                new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=img_data)

            return output_doc.tobytes()
        finally:
            output_doc.close()
    finally:
        doc.close()
