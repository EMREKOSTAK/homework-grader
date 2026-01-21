"""Tests for deterministic checks."""

import pytest
from app.services.pptx_parser import PPTXParser
from app.services.deterministic_checks import DeterministicChecker


class TestPageNumberCheck:
    """Test page number detection."""

    def test_detects_page_numbers_top_right(self, sample_ethics_pptx):
        """Test that page numbers in top-right are detected."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        result = checker.check_page_numbers(parsed)

        # Sample has page numbers on all slides
        assert result.passed is True
        assert result.score > 0
        assert len(result.evidence) > 0

    def test_missing_page_numbers(self, create_test_pptx):
        """Test detection of missing page numbers."""
        # Create slides without page numbers
        slides = [
            {"texts": [("Content only", 1, 1, 8, 1)]},
            {"texts": [("More content", 1, 1, 8, 1)]},
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_page_numbers(parsed)

        assert result.passed is False
        assert result.score == 0
        assert len(result.missing_items) == 2

    def test_page_number_formats(self, create_test_pptx):
        """Test various page number formats are recognized."""
        # Test "X" format
        slides_single = [{"texts": [("5", 9.2, 0.2, 0.5, 0.3)]}]

        # Test "X/Y" format
        slides_fraction = [{"texts": [("3/10", 9.2, 0.2, 0.5, 0.3)]}]

        # Test "X / Y" format with spaces
        slides_spaced = [{"texts": [("3 / 10", 9.2, 0.2, 0.5, 0.3)]}]

        parser = PPTXParser()
        checker = DeterministicChecker()

        for slides in [slides_single, slides_fraction, slides_spaced]:
            pptx_bytes = create_test_pptx(slides)
            parsed = parser.parse(pptx_bytes)
            result = checker.check_page_numbers(parsed)
            assert result.passed is True, f"Failed for format: {slides[0]['texts'][0][0]}"


class TestEthicsPrinciplesCheck:
    """Test ethics principles detection."""

    def test_detects_multiple_principles(self, sample_ethics_pptx):
        """Test that multiple ethics principles are detected."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        result = checker.check_ethics_principles(parsed)

        # Sample has 5 principles
        assert result.passed is True
        assert result.score >= 10
        assert len(result.evidence) >= 5

    def test_detects_turkish_keywords(self, create_test_pptx):
        """Test detection of Turkish ethics keywords."""
        slides = [
            {
                "texts": [
                    ("Bu filmde adalet kavramı önemlidir.", 1, 1, 8, 1),
                    ("Özerklik ve bireysel haklar vurgulanmıştır.", 1, 2, 8, 1),
                    ("Yararseverlik ilkesi açısından değerlendirilmiştir.", 1, 3, 8, 1),
                    ("Zarar vermeme prensibi gözetilmiştir.", 1, 4, 8, 1),
                    ("Dürüstlük her zaman önemlidir.", 1, 5, 8, 1),
                ]
            }
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_ethics_principles(parsed)

        assert result.passed is True
        assert "adalet" in result.details.lower()

    def test_insufficient_principles(self, create_test_pptx):
        """Test detection fails with insufficient principles."""
        slides = [
            {
                "texts": [
                    ("Sadece adalet kavramı bahsedilmiştir.", 1, 1, 8, 1),
                ]
            }
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_ethics_principles(parsed)

        assert result.passed is False
        assert result.score < 10
        assert len(result.missing_items) > 0

    def test_english_keywords_also_work(self, create_test_pptx):
        """Test that English keywords are also detected."""
        slides = [
            {
                "texts": [
                    ("Justice is important in this film.", 1, 1, 8, 1),
                    ("Autonomy and rights are discussed.", 1, 2, 8, 1),
                    ("Beneficence is a key theme.", 1, 3, 8, 1),
                    ("Nonmaleficence is also present.", 1, 4, 8, 1),
                    ("Honesty and transparency matter.", 1, 5, 8, 1),
                ]
            }
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_ethics_principles(parsed)

        assert result.passed is True


class TestTemplateFieldsCheck:
    """Test template fields detection."""

    def test_detects_all_fields(self, sample_ethics_pptx):
        """Test that all template fields are detected."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        result = checker.check_template_fields(parsed)

        assert result.passed is True
        assert len(result.missing_items) <= 1  # Allow one missing
        assert result.score > 8

    def test_missing_fields_detected(self, create_test_pptx):
        """Test that missing fields are reported."""
        # Only include film name, nothing else
        slides = [{"texts": [("Film Adı: Test Film", 1, 1, 8, 1)]}]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_template_fields(parsed)

        assert result.passed is False
        assert len(result.missing_items) >= 4  # At least 4 missing
        assert "Tür" in result.missing_items or "Yönetmen" in result.missing_items

    def test_field_variations_detected(self, create_test_pptx):
        """Test that variations of field names are detected."""
        slides = [
            {
                "texts": [
                    ("Movie Name: Test Film", 1, 1, 8, 1),  # English
                    ("Genre: Drama", 1, 2, 8, 1),  # English
                    ("Director: John Doe", 1, 3, 8, 1),  # English
                    ("Writer: Jane Doe", 1, 4, 8, 1),  # English
                    ("Cast: Actor 1, Actor 2", 1, 5, 8, 1),  # English variation
                    ("My thoughts on this film", 1, 6, 8, 1),  # English
                ]
            }
        ]
        pptx_bytes = create_test_pptx(slides)

        parser = PPTXParser()
        parsed = parser.parse(pptx_bytes)

        checker = DeterministicChecker()
        result = checker.check_template_fields(parsed)

        # Should detect most fields even with English keywords
        assert result.score > 5


class TestAllChecks:
    """Test running all checks together."""

    def test_run_all_checks(self, sample_ethics_pptx):
        """Test that all checks run successfully."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        results = checker.run_all_checks(parsed)

        assert len(results) == 3
        check_names = [r.check_name for r in results]
        assert "page_numbers" in check_names
        assert "ethics_principles" in check_names
        assert "template_fields" in check_names

    def test_get_all_text_content(self, sample_ethics_pptx):
        """Test getting all text content."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        all_text = checker.get_all_text_content(parsed)

        assert "Film Analizi" in all_text
        assert "Etik İlkeleri" in all_text
        assert "Slayt 1" in all_text

    def test_get_slide_text_map(self, sample_ethics_pptx):
        """Test getting slide text map."""
        parser = PPTXParser()
        parsed = parser.parse(sample_ethics_pptx)

        checker = DeterministicChecker()
        text_map = checker.get_slide_text_map(parsed)

        assert len(text_map) == 5
        assert 1 in text_map
        assert 5 in text_map
        assert isinstance(text_map[1], list)
