"""Tests for PPTX parser."""

import pytest
from app.services.pptx_parser import PPTXParser


class TestPPTXParser:
    """Test suite for PPTXParser."""

    def test_parse_minimal_pptx(self, minimal_pptx):
        """Test parsing a minimal PPTX file."""
        parser = PPTXParser()
        result = parser.parse(minimal_pptx)

        assert result.meta.total_slides == 1
        assert result.meta.slide_width > 0
        assert result.meta.slide_height > 0
        assert result.meta.units == "EMU"

    def test_parse_extracts_text(self, minimal_pptx):
        """Test that text content is extracted."""
        parser = PPTXParser()
        result = parser.parse(minimal_pptx)

        assert len(result.slides) == 1
        slide = result.slides[0]
        assert slide.slide_no == 1

        # Should have at least one text element
        assert len(slide.elements) >= 1

        # Find the test text
        texts = [elem.text for elem in slide.elements]
        assert "Test Slide" in texts

    def test_parse_ethics_pptx(self, sample_ethics_pptx):
        """Test parsing the sample ethics PPTX."""
        parser = PPTXParser()
        result = parser.parse(sample_ethics_pptx)

        assert result.meta.total_slides == 5

        # Check slide numbers are correct
        for i, slide in enumerate(result.slides, start=1):
            assert slide.slide_no == i

    def test_text_normalization(self, create_test_pptx):
        """Test that text is properly normalized."""
        slides = [
            {
                "texts": [
                    ("  Multiple   spaces   here  ", 1, 1, 8, 1),
                ]
            }
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        result = parser.parse(pptx_bytes)

        # Normalized text should have collapsed whitespace
        texts = [elem.text for elem in result.slides[0].elements]
        assert "Multiple spaces here" in texts

    def test_element_has_bbox(self, minimal_pptx):
        """Test that elements have bounding box information."""
        parser = PPTXParser()
        result = parser.parse(minimal_pptx)

        for slide in result.slides:
            for element in slide.elements:
                assert hasattr(element, "bbox")
                assert element.bbox.x >= 0
                assert element.bbox.y >= 0
                assert element.bbox.w >= 0
                assert element.bbox.h >= 0

    def test_element_has_id(self, minimal_pptx):
        """Test that elements have unique IDs."""
        parser = PPTXParser()
        result = parser.parse(minimal_pptx)

        ids = set()
        for slide in result.slides:
            for element in slide.elements:
                assert element.id is not None
                assert element.id not in ids
                ids.add(element.id)

    def test_raw_text_preserved(self, create_test_pptx):
        """Test that raw text is preserved for evidence."""
        original_text = "Original  Text  Here"
        slides = [{"texts": [(original_text, 1, 1, 8, 1)]}]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        result = parser.parse(pptx_bytes)

        # Find the element
        element = result.slides[0].elements[0]

        # raw_text should preserve original formatting
        assert element.raw_text == original_text.strip()

    def test_search_text(self, sample_ethics_pptx):
        """Test text search functionality."""
        parser = PPTXParser()
        result = parser.parse(sample_ethics_pptx)

        # Search for "adalet"
        matches = parser.search_text(result, r"adalet", case_sensitive=False)

        assert len(matches) > 0
        slide_nos = [m[0] for m in matches]
        assert 3 in slide_nos  # Ethics principles slide

    def test_get_text_in_region(self, sample_ethics_pptx):
        """Test getting text from a specific region."""
        parser = PPTXParser()
        result = parser.parse(sample_ethics_pptx)

        # Get text from top-right region (where page numbers are)
        for slide in result.slides:
            top_right = parser.get_text_in_region(
                slide_data=slide,
                deck_meta=result.meta,
                x_min_ratio=0.85,
                x_max_ratio=1.0,
                y_min_ratio=0.0,
                y_max_ratio=0.15,
            )
            # Should find page numbers in top-right
            page_num_texts = [e.text for e in top_right]
            # At least some slides should have page numbers
            # (the sample has them)


class TestPPTXParserEdgeCases:
    """Test edge cases for the parser."""

    def test_empty_slide(self, create_test_pptx):
        """Test handling of empty slides."""
        slides = [{"texts": []}]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        result = parser.parse(pptx_bytes)

        assert result.meta.total_slides == 1
        assert len(result.slides) == 1
        assert len(result.slides[0].elements) == 0

    def test_multiple_empty_slides(self, create_test_pptx):
        """Test multiple empty slides."""
        slides = [{"texts": []}, {"texts": []}, {"texts": []}]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        result = parser.parse(pptx_bytes)

        assert result.meta.total_slides == 3
        assert len(result.slides) == 3

    def test_unicode_content(self, create_test_pptx):
        """Test handling of Turkish/Unicode characters."""
        turkish_text = "Türkçe karakterler: ğüşıöç ĞÜŞİÖÇ"
        slides = [{"texts": [(turkish_text, 1, 1, 8, 1)]}]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        result = parser.parse(pptx_bytes)

        texts = [elem.text for elem in result.slides[0].elements]
        assert turkish_text in texts
