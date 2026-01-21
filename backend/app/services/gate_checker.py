"""Gate Checker - Basic validation before AI processing."""

from typing import Tuple
from app.models.schemas import ParsedPPTX
from app.services.pptx_parser import PPTXParser


class GateChecker:
    """Performs basic validation checks before sending to AI."""

    # Minimum character count for content
    MIN_TEXT_LENGTH = 300

    # Maximum file size (15MB)
    MAX_FILE_SIZE = 15 * 1024 * 1024

    def __init__(self):
        self.parser = PPTXParser()

    def validate_file(self, file_content: bytes) -> Tuple[bool, str, ParsedPPTX | None]:
        """
        Validate a PPTX file before AI processing.

        Returns:
            Tuple of (is_valid, error_message, parsed_pptx)
        """
        # 1. Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            return False, f"Dosya boyutu çok büyük. Maksimum: {self.MAX_FILE_SIZE // (1024*1024)}MB", None

        # 2. Check PPTX format (ZIP signature)
        if not file_content[:4] == b'PK\x03\x04':
            return False, "Geçersiz PPTX dosyası", None

        # 3. Try to parse
        try:
            parsed_pptx = self.parser.parse(file_content)
        except Exception as e:
            return False, f"PPTX ayrıştırma hatası: {str(e)}", None

        # 4. Check slide count
        if parsed_pptx.meta.total_slides == 0:
            return False, "Sunum boş veya slayt içermiyor", None

        # 5. Check minimum content
        total_text = self._get_total_text_length(parsed_pptx)
        if total_text < self.MIN_TEXT_LENGTH:
            return False, f"Yetersiz içerik. Minimum {self.MIN_TEXT_LENGTH} karakter gerekli, {total_text} karakter bulundu", None

        return True, "OK", parsed_pptx

    def _get_total_text_length(self, parsed_pptx: ParsedPPTX) -> int:
        """Get total text length across all slides."""
        total = 0
        for slide in parsed_pptx.slides:
            for element in slide.elements:
                total += len(element.text)
        return total

    def get_content_stats(self, parsed_pptx: ParsedPPTX) -> dict:
        """Get content statistics for the presentation."""
        total_text = self._get_total_text_length(parsed_pptx)
        slide_count = parsed_pptx.meta.total_slides

        return {
            "total_slides": slide_count,
            "total_characters": total_text,
            "avg_chars_per_slide": total_text / slide_count if slide_count > 0 else 0,
        }
