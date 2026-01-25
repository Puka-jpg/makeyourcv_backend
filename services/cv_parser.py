"""
CV Parser Service - Extracts raw text from PDF resumes.
"""

from io import BytesIO

from PyPDF2 import PdfReader

from utils.logger import get_logger

logger = get_logger()


class CVParserService:
    """Service for extracting raw text from PDF resumes."""

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extracts raw text from a PDF file.

        Args:
            file_content: PDF file content as bytes

        Returns:
            Extracted text as a string

        Raises:
            ValueError: If PDF extraction fails
        """
        try:
            reader = PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error("Error extracting text from PDF:", extra={"error": str(e)})
            raise ValueError("Could not extract text from the provided PDF file.")
