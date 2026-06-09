import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import fitz
from fastapi.testclient import TestClient

from api.main import MAX_UPLOAD_BYTES, app
from flatten_pdf import flatten_pdf
from lib.flatten import EmptyPdfError, InvalidPdfError, flatten_pdf_bytes


def create_dummy_pdf_bytes(text="This is a dummy PDF for testing flattening."):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=20)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_dummy_pdf(filename="dummy.pdf"):
    pdf_bytes = create_dummy_pdf_bytes()
    with open(filename, "wb") as pdf_file:
        pdf_file.write(pdf_bytes)
    return filename


class FlattenBytesTests(unittest.TestCase):
    def test_flatten_pdf_bytes_returns_valid_pdf(self):
        pdf_bytes = create_dummy_pdf_bytes()
        output_bytes = flatten_pdf_bytes(pdf_bytes, dpi=150, jpg_quality=75)

        self.assertTrue(output_bytes.startswith(b"%PDF"))
        self.assertGreater(len(output_bytes), 0)

        output_doc = fitz.open(stream=output_bytes, filetype="pdf")
        self.assertEqual(len(output_doc), 1)
        output_doc.close()

    def test_empty_pdf_raises(self):
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0

        with patch("lib.flatten.fitz.open", return_value=mock_doc):
            with self.assertRaises(EmptyPdfError):
                flatten_pdf_bytes(b"%PDF-1.4")

    def test_invalid_pdf_raises(self):
        with self.assertRaises(InvalidPdfError):
            flatten_pdf_bytes(b"not-a-pdf")


class FlattenCliTests(unittest.TestCase):
    def test_cli_flatten_writes_output_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, "dummy.pdf")
            create_dummy_pdf(pdf_path)
            flatten_pdf(pdf_path)

            expected_output = os.path.join(temp_dir, "dummy-flat-150.pdf")
            self.assertTrue(os.path.exists(expected_output))
            self.assertGreater(os.path.getsize(expected_output), 0)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_flatten_endpoint_happy_path(self):
        pdf_bytes = create_dummy_pdf_bytes()
        response = self.client.post(
            "/api/flatten",
            files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
            data={"dpi": "150", "jpg_quality": "75"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertIn('filename="sample-flat-150.pdf"', response.headers["content-disposition"])

    def test_flatten_endpoint_rejects_non_pdf(self):
        response = self.client.post(
            "/api/flatten",
            files={"file": ("notes.txt", b"hello", "text/plain")},
            data={"dpi": "150", "jpg_quality": "75"},
        )

        self.assertEqual(response.status_code, 415)

    def test_flatten_endpoint_rejects_oversize_upload(self):
        pdf_bytes = create_dummy_pdf_bytes()
        with patch("api.main.MAX_UPLOAD_BYTES", 16):
            response = self.client.post(
                "/api/flatten",
                files={"file": ("large.pdf", pdf_bytes, "application/pdf")},
                data={"dpi": "150", "jpg_quality": "75"},
            )

        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
