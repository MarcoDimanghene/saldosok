import os
import tempfile
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

import fitz
from fastapi import HTTPException, UploadFile
from PIL import UnidentifiedImageError

from back.routes.extract import _store_upload, _validate_image
from engine.extract import (
    DocumentPageLimitError,
    DocumentPixelLimitError,
    MAX_PDF_PAGES,
    get_text,
    ocr_pdf,
)


class UploadLimitTests(unittest.TestCase):
    def test_streaming_upload_stops_when_size_limit_is_exceeded(self):
        upload = UploadFile(
            file=BytesIO(b"0123456789abcdef"),
            filename="invoice.pdf",
        )

        with patch("back.routes.extract.MAX_UPLOAD_SIZE_BYTES", 8):
            with self.assertRaises(HTTPException) as error:
                _store_upload(upload, ".pdf")

        self.assertEqual(error.exception.status_code, 413)

    def test_empty_upload_is_rejected(self):
        upload = UploadFile(file=BytesIO(b""), filename="invoice.pdf")

        with self.assertRaises(HTTPException) as error:
            _store_upload(upload, ".pdf")

        self.assertEqual(error.exception.status_code, 400)

    def test_invalid_image_content_is_rejected(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
            image_file.write(b"not an image")
            image_path = image_file.name

        try:
            with self.assertRaises(UnidentifiedImageError):
                _validate_image(image_path)
        finally:
            os.unlink(image_path)

    def test_image_pixel_limit_is_checked_before_ocr(self):
        image = MagicMock()
        image.__enter__.return_value.width = 7000
        image.__enter__.return_value.height = 7000

        with patch("back.routes.extract.Image.open", return_value=image):
            with self.assertRaises(HTTPException) as error:
                _validate_image("unused.png")

        self.assertEqual(error.exception.status_code, 413)
        image.__enter__.return_value.verify.assert_not_called()

    def test_pdf_page_limit_is_checked_before_ocr(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            pdf_path = pdf_file.name

        try:
            with fitz.open() as document:
                for _ in range(MAX_PDF_PAGES + 1):
                    document.new_page()
                document.save(pdf_path)

            with self.assertRaises(DocumentPageLimitError):
                get_text(pdf_path)
        finally:
            os.unlink(pdf_path)

    def test_ocr_rejects_oversized_pdf_page_before_rendering(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            pdf_path = pdf_file.name

        try:
            with fitz.open() as document:
                document.new_page(width=3000, height=3000)
                document.save(pdf_path)

            with self.assertRaises(DocumentPixelLimitError):
                ocr_pdf(pdf_path)
        finally:
            os.unlink(pdf_path)


if __name__ == "__main__":
    unittest.main()
