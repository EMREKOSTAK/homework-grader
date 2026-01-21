"""Tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError
from app.models.schemas import (
    TextElement,
    SlideData,
    DeckMeta,
    ParsedPPTX,
    BoundingBox,
    TextStyle,
    EvidenceItem,
    DeterministicCheckResult,
    RubricScore,
    GradingResult,
    ImprovementSuggestion,
    LLMGradingResponse,
    LLMRubricScore,
)


class TestBoundingBox:
    """Test BoundingBox schema."""

    def test_valid_bbox(self):
        """Test valid bounding box creation."""
        bbox = BoundingBox(x=100, y=200, w=300, h=400)
        assert bbox.x == 100
        assert bbox.y == 200

    def test_bbox_with_floats(self):
        """Test bounding box with float values."""
        bbox = BoundingBox(x=100.5, y=200.5, w=300.5, h=400.5)
        assert bbox.x == 100.5


class TestTextElement:
    """Test TextElement schema."""

    def test_valid_text_element(self):
        """Test valid text element creation."""
        elem = TextElement(
            id="test123",
            type="text",
            text="Hello World",
            raw_text="Hello World",
            bbox=BoundingBox(x=0, y=0, w=100, h=50),
        )
        assert elem.id == "test123"
        assert elem.text == "Hello World"

    def test_text_element_with_style(self):
        """Test text element with style."""
        elem = TextElement(
            id="test123",
            type="text",
            text="Bold Text",
            raw_text="Bold Text",
            bbox=BoundingBox(x=0, y=0, w=100, h=50),
            style=TextStyle(font_size=12.0, bold=True),
        )
        assert elem.style.bold is True
        assert elem.style.font_size == 12.0


class TestSlideData:
    """Test SlideData schema."""

    def test_valid_slide(self):
        """Test valid slide creation."""
        slide = SlideData(slide_no=1, elements=[])
        assert slide.slide_no == 1
        assert len(slide.elements) == 0

    def test_slide_with_elements(self):
        """Test slide with elements."""
        elem = TextElement(
            id="e1",
            type="text",
            text="Test",
            raw_text="Test",
            bbox=BoundingBox(x=0, y=0, w=100, h=50),
        )
        slide = SlideData(slide_no=1, elements=[elem])
        assert len(slide.elements) == 1

    def test_invalid_slide_number(self):
        """Test that slide_no must be >= 1."""
        with pytest.raises(ValidationError):
            SlideData(slide_no=0, elements=[])


class TestDeckMeta:
    """Test DeckMeta schema."""

    def test_valid_meta(self):
        """Test valid deck meta creation."""
        meta = DeckMeta(
            slide_width=9144000,
            slide_height=6858000,
            units="EMU",
            total_slides=5,
        )
        assert meta.total_slides == 5

    def test_invalid_total_slides(self):
        """Test that total_slides must be >= 0."""
        with pytest.raises(ValidationError):
            DeckMeta(
                slide_width=100,
                slide_height=100,
                total_slides=-1,
            )


class TestEvidenceItem:
    """Test EvidenceItem schema."""

    def test_valid_evidence(self):
        """Test valid evidence creation."""
        evidence = EvidenceItem(
            slide_no=3,
            quote="This is the quoted text",
            context="Found in header",
        )
        assert evidence.slide_no == 3
        assert "quoted" in evidence.quote

    def test_evidence_optional_context(self):
        """Test evidence without context."""
        evidence = EvidenceItem(
            slide_no=1,
            quote="Quote only",
        )
        assert evidence.context is None


class TestDeterministicCheckResult:
    """Test DeterministicCheckResult schema."""

    def test_valid_check_result(self):
        """Test valid check result."""
        result = DeterministicCheckResult(
            check_name="page_numbers",
            passed=True,
            score=5.0,
            max_score=5.0,
            evidence=[],
            missing_items=[],
        )
        assert result.passed is True
        assert result.score == 5.0

    def test_check_result_with_evidence(self):
        """Test check result with evidence."""
        evidence = EvidenceItem(slide_no=1, quote="1/5")
        result = DeterministicCheckResult(
            check_name="page_numbers",
            passed=True,
            score=5.0,
            max_score=5.0,
            evidence=[evidence],
            missing_items=[],
            details="All slides have page numbers",
        )
        assert len(result.evidence) == 1


class TestRubricScore:
    """Test RubricScore schema."""

    def test_valid_rubric_score(self):
        """Test valid rubric score."""
        score = RubricScore(
            category="Ethics Principles",
            score=12.0,
            max_score=15.0,
            reason="Good coverage of principles",
            evidence=[],
        )
        assert score.score == 12.0

    def test_rubric_score_with_sub_scores(self):
        """Test rubric score with sub-scores."""
        score = RubricScore(
            category="Scene Explanation",
            score=40.0,
            max_score=50.0,
            reason="Good explanation",
            evidence=[],
            sub_scores={
                "specificity": 18.0,
                "coherence": 12.0,
                "ethical_link": 10.0,
            },
        )
        assert score.sub_scores["specificity"] == 18.0


class TestGradingResult:
    """Test GradingResult schema."""

    def test_valid_grading_result(self):
        """Test valid grading result."""
        rubric_score = RubricScore(
            category="Test",
            score=10.0,
            max_score=10.0,
            reason="Good",
            evidence=[],
        )
        result = GradingResult(
            total_score=85.0,
            rubric_scores=[rubric_score],
            missing_items=[],
            improvements=[],
            deterministic_checks=[],
            on_time_submitted=True,
        )
        assert result.total_score == 85.0
        assert result.on_time_submitted is True

    def test_grading_result_score_bounds(self):
        """Test that total_score must be 0-100."""
        with pytest.raises(ValidationError):
            GradingResult(
                total_score=150.0,  # Invalid
                rubric_scores=[],
                missing_items=[],
                improvements=[],
                deterministic_checks=[],
            )


class TestLLMGradingResponse:
    """Test LLM response schema validation."""

    def test_valid_llm_response(self):
        """Test valid LLM response parsing."""
        llm_score = LLMRubricScore(
            kategori="Etik İlkeleri",
            puan=12.0,
            max_puan=15.0,
            aciklama="İyi bir açıklama",
            kanitlar=[{"slayt_no": 3, "alinti": "Test quote"}],
        )
        response = LLMGradingResponse(
            toplam_puan=75.0,
            rubrik_puanlari=[llm_score],
            eksik_ogeler=["Item 1"],
            iyilestirme_onerileri=[],
        )
        assert response.toplam_puan == 75.0

    def test_llm_response_with_improvements(self):
        """Test LLM response with improvements."""
        response = LLMGradingResponse(
            toplam_puan=60.0,
            rubrik_puanlari=[],
            eksik_ogeler=[],
            iyilestirme_onerileri=[
                {"kategori": "Scene", "oneri": "Add more detail", "oncelik": "yuksek"}
            ],
            notlar="General notes here",
        )
        assert len(response.iyilestirme_onerileri) == 1


class TestImprovementSuggestion:
    """Test ImprovementSuggestion schema."""

    def test_valid_improvement(self):
        """Test valid improvement suggestion."""
        imp = ImprovementSuggestion(
            category="Scene Explanation",
            suggestion="Add more specific details about characters",
            priority="high",
        )
        assert imp.priority == "high"

    def test_default_priority(self):
        """Test default priority value."""
        imp = ImprovementSuggestion(
            category="Visual Design",
            suggestion="Improve contrast",
        )
        assert imp.priority == "medium"
