"""Pydantic models for the homework grading application."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box for an element on a slide."""
    x: float = Field(..., description="X position in EMUs or normalized")
    y: float = Field(..., description="Y position in EMUs or normalized")
    w: float = Field(..., description="Width in EMUs or normalized")
    h: float = Field(..., description="Height in EMUs or normalized")


class TextStyle(BaseModel):
    """Style information for text elements."""
    font_size: Optional[float] = Field(None, description="Font size in points")
    bold: Optional[bool] = Field(None, description="Whether text is bold")
    font_name: Optional[str] = Field(None, description="Font family name")


class TextElement(BaseModel):
    """A text element extracted from a slide."""
    id: str = Field(..., description="Unique identifier for the element")
    type: str = Field(default="text", description="Element type")
    text: str = Field(..., description="Extracted and normalized text content")
    raw_text: str = Field(..., description="Original text for evidence quotes")
    bbox: BoundingBox = Field(..., description="Position and size")
    style: TextStyle = Field(default_factory=TextStyle, description="Text styling")


class SlideData(BaseModel):
    """Data for a single slide."""
    slide_no: int = Field(..., ge=1, description="1-indexed slide number")
    elements: List[TextElement] = Field(default_factory=list, description="Text elements on slide")


class DeckMeta(BaseModel):
    """Metadata about the presentation deck."""
    slide_width: float = Field(..., description="Slide width in EMUs")
    slide_height: float = Field(..., description="Slide height in EMUs")
    units: str = Field(default="EMU", description="Unit of measurement")
    total_slides: int = Field(..., ge=0, description="Total number of slides")


class ParsedPPTX(BaseModel):
    """Complete parsed PPTX structure."""
    meta: DeckMeta = Field(..., description="Deck metadata")
    slides: List[SlideData] = Field(default_factory=list, description="All slides data")


class EvidenceItem(BaseModel):
    """Evidence quote from the presentation."""
    slide_no: int = Field(..., description="Slide number where evidence was found")
    quote: str = Field(..., description="Quoted text from the slide")
    context: Optional[str] = Field(None, description="Additional context")
    comment: Optional[str] = Field(None, description="AI's comment/evaluation about this evidence")


class DeterministicCheckResult(BaseModel):
    """Result of a deterministic check."""
    check_name: str = Field(..., description="Name of the check")
    passed: bool = Field(..., description="Whether the check passed")
    score: float = Field(..., ge=0, description="Points awarded")
    max_score: float = Field(..., ge=0, description="Maximum possible points")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting evidence")
    missing_items: List[str] = Field(default_factory=list, description="Items that were not found")
    details: Optional[str] = Field(None, description="Additional details")


class DetectedEthicsPrinciple(BaseModel):
    """Evaluation of a detected ethics principle."""
    principle: str = Field(..., description="Name of the ethics principle")
    correct_definition: bool = Field(..., description="Whether the definition is correct")
    scene_match: bool = Field(..., description="Whether the scene matches the principle")
    note: Optional[str] = Field(None, description="Additional notes about this principle")


class RubricScore(BaseModel):
    """Score for a single rubric item."""
    category: str = Field(..., description="Rubric category name")
    score: float = Field(..., ge=0, description="Points awarded")
    max_score: float = Field(..., ge=0, description="Maximum possible points")
    reason: str = Field(..., description="Short explanation for the score")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Evidence quotes")
    sub_scores: Optional[Dict[str, float]] = Field(None, description="Sub-category scores")
    # Extended fields for detailed evaluation
    detected_principles: Optional[List[DetectedEthicsPrinciple]] = Field(None, description="Detected ethics principles with evaluation")
    consistency_analysis: Optional[str] = Field(None, description="Analysis of internal consistency")
    found_fields: Optional[List[str]] = Field(None, description="Template fields that were found")
    missing_fields: Optional[List[str]] = Field(None, description="Template fields that are missing")
    language_errors: Optional[List[str]] = Field(None, description="Detected language/grammar errors")


class ImprovementSuggestion(BaseModel):
    """Actionable improvement suggestion."""
    category: str = Field(..., description="Related rubric category")
    suggestion: str = Field(..., description="Specific improvement suggestion")
    priority: str = Field(default="medium", description="Priority: high, medium, low")


class GradingResult(BaseModel):
    """Complete grading result."""
    total_score: float = Field(..., ge=0, le=100, description="Total score out of 100")
    rubric_scores: List[RubricScore] = Field(..., description="Individual rubric scores")
    missing_items: List[str] = Field(default_factory=list, description="Missing required items")
    improvements: List[ImprovementSuggestion] = Field(default_factory=list, description="Improvement suggestions")
    deterministic_checks: List[DeterministicCheckResult] = Field(default_factory=list, description="Deprecated - no longer used")
    on_time_submitted: bool = Field(default=False, description="Whether submitted on time")
    grading_notes: Optional[str] = Field(None, description="Additional grading notes")
    overall_evaluation: Optional[str] = Field(None, description="Overall quality assessment of the presentation")


class StudentResult(BaseModel):
    """Result for a single student in bulk grading."""
    student_name: str = Field(..., description="Student name extracted from filename")
    filename: str = Field(..., description="Original filename")
    success: bool = Field(..., description="Whether grading succeeded")
    result: Optional[GradingResult] = Field(None, description="Grading result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")


class BulkAnalyzeResponse(BaseModel):
    """Response from the bulk analyze endpoint."""
    total_files: int = Field(..., description="Total number of files processed")
    successful: int = Field(..., description="Number of successfully graded files")
    failed: int = Field(..., description="Number of failed files")
    results: List[StudentResult] = Field(..., description="Individual results for each student")


class AnalyzeRequest(BaseModel):
    """Request for analysis (used for JSON body, file comes separately)."""
    on_time: bool = Field(default=False, description="Whether submission was on time")


class AnalyzeResponse(BaseModel):
    """Response from the analyze endpoint."""
    success: bool = Field(..., description="Whether analysis succeeded")
    result: Optional[GradingResult] = Field(None, description="Grading result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    parsed_content: Optional[ParsedPPTX] = Field(None, description="Parsed PPTX for debugging")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


# LLM Response Schema - This is what we expect from the LLM
class LLMDetectedPrinciple(BaseModel):
    """LLM's evaluation of a detected ethics principle."""
    ilke: str = Field(..., description="Principle name")
    dogru_tanim: bool = Field(default=True, description="Is definition correct")
    sahne_uyumu: bool = Field(default=True, description="Does scene match")
    not_: Optional[str] = Field(None, alias="not", description="Additional note")

    class Config:
        populate_by_name = True


class LLMRubricScore(BaseModel):
    """LLM's score for a rubric item."""
    kategori: str = Field(..., description="Rubric category name in Turkish")
    puan: float = Field(..., ge=0, description="Points awarded")
    max_puan: float = Field(..., ge=0, description="Maximum points")
    aciklama: str = Field(..., description="Reason in Turkish")
    kanitlar: List[Dict[str, Any]] = Field(default_factory=list, description="Evidence list")
    alt_puanlar: Optional[Dict[str, float]] = Field(None, description="Sub-scores")
    # Extended fields
    tespit_edilen_ilkeler: Optional[List[Dict[str, Any]]] = Field(None, description="Detected principles")
    tutarlilik_analizi: Optional[str] = Field(None, description="Consistency analysis")
    bulunan_alanlar: Optional[List[str]] = Field(None, description="Found fields")
    eksik_alanlar: Optional[List[str]] = Field(None, description="Missing fields")
    dil_hatalari: Optional[List[str]] = Field(None, description="Language errors")


class LLMGradingResponse(BaseModel):
    """Expected response structure from the LLM."""
    toplam_puan: float = Field(..., ge=0, le=100, description="Total score")
    rubrik_puanlari: List[LLMRubricScore] = Field(..., description="Rubric scores")
    eksik_ogeler: List[str] = Field(default_factory=list, description="Missing items")
    iyilestirme_onerileri: List[Dict[str, str]] = Field(default_factory=list, description="Improvements")
    notlar: Optional[str] = Field(None, description="Additional notes")
    genel_degerlendirme: Optional[str] = Field(None, description="Overall evaluation")
