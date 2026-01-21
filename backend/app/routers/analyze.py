"""Analyze router - handles PPTX upload and grading."""

import io
import logging
import re
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    AnalyzeResponse,
    ParsedPPTX,
    BulkAnalyzeResponse,
    StudentResult,
    GradingResult,
)
from app.services.gate_checker import GateChecker
from app.services.llm_grader import LLMGrader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])

# Maximum file size: 15MB
MAX_FILE_SIZE = 15 * 1024 * 1024


def extract_student_name(filename: str) -> str:
    """Extract student name from filename (isim_soyisim.pptx -> Isim Soyisim)."""
    # Remove .pptx extension
    name = filename.lower().replace(".pptx", "")

    # Replace underscores with spaces
    name = name.replace("_", " ")

    # Title case
    name = name.title()

    return name


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_presentation(
    file: UploadFile = File(..., description="PPTX file to analyze"),
    on_time: bool = Form(default=False, description="Whether submission was on time"),
):
    """
    Analyze a PPTX presentation and return grading results.

    - **file**: The PowerPoint (.pptx) file to analyze
    - **on_time**: Boolean indicating if the submission was on time (adds 10 points)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Dosya adı gerekli")

    if not file.filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=400,
            detail="Sadece .pptx dosyaları kabul edilir"
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=400, detail="Dosya okunamadı")

    try:
        # Gate check (basic validation)
        gate_checker = GateChecker()
        is_valid, error_msg, parsed_pptx = gate_checker.validate_file(content)

        if not is_valid:
            return AnalyzeResponse(
                success=False,
                result=None,
                error=error_msg,
                parsed_content=None,
            )

        # Run LLM grading (all content evaluation is done by AI)
        grader = LLMGrader()
        grading_result = await grader.grade(
            parsed_pptx=parsed_pptx,
            on_time=on_time,
        )

        return AnalyzeResponse(
            success=True,
            result=grading_result,
            error=None,
            parsed_content=None,
        )

    except ValueError as e:
        logger.error(f"Grading error: {e}")
        return AnalyzeResponse(
            success=False,
            result=None,
            error=str(e),
            parsed_content=None,
        )
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analiz sırasında beklenmeyen hata: {str(e)}"
        )


@router.post("/analyze-bulk", response_model=BulkAnalyzeResponse)
async def analyze_bulk(
    files: List[UploadFile] = File(..., description="Multiple PPTX files to analyze"),
    on_time: bool = Form(default=False, description="Whether submissions were on time"),
):
    """
    Analyze multiple PPTX presentations in bulk.

    Filenames should be in format: isim_soyisim.pptx

    - **files**: List of PowerPoint (.pptx) files to analyze
    - **on_time**: Boolean indicating if submissions were on time (adds 10 points)
    """
    results: List[StudentResult] = []
    gate_checker = GateChecker()
    grader = LLMGrader()

    for file in files:
        filename = file.filename or "unknown.pptx"
        student_name = extract_student_name(filename)

        # Skip non-pptx files
        if not filename.lower().endswith(".pptx"):
            results.append(StudentResult(
                student_name=student_name,
                filename=filename,
                success=False,
                result=None,
                error="Sadece .pptx dosyaları kabul edilir",
            ))
            continue

        try:
            content = await file.read()

            # Gate check
            is_valid, error_msg, parsed_pptx = gate_checker.validate_file(content)

            if not is_valid:
                results.append(StudentResult(
                    student_name=student_name,
                    filename=filename,
                    success=False,
                    result=None,
                    error=error_msg,
                ))
                continue

            # LLM grading
            grading_result = await grader.grade(
                parsed_pptx=parsed_pptx,
                on_time=on_time,
            )

            results.append(StudentResult(
                student_name=student_name,
                filename=filename,
                success=True,
                result=grading_result,
                error=None,
            ))

        except Exception as e:
            logger.exception(f"Error processing {filename}: {e}")
            results.append(StudentResult(
                student_name=student_name,
                filename=filename,
                success=False,
                result=None,
                error=str(e),
            ))

    successful = sum(1 for r in results if r.success)

    return BulkAnalyzeResponse(
        total_files=len(results),
        successful=successful,
        failed=len(results) - successful,
        results=results,
    )


@router.post("/export-excel")
async def export_excel(
    files: List[UploadFile] = File(..., description="Multiple PPTX files to analyze"),
    on_time: bool = Form(default=False, description="Whether submissions were on time"),
):
    """
    Analyze multiple PPTX presentations and return results as Excel file.

    Filenames should be in format: isim_soyisim.pptx
    """
    import xlsxwriter

    # First, run bulk analysis
    bulk_response = await analyze_bulk(files=files, on_time=on_time)

    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Add summary worksheet
    summary_sheet = workbook.add_worksheet("Özet")

    # Formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })

    cell_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })

    text_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True,
    })

    success_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'font_color': '#006100',
        'align': 'center',
    })

    error_format = workbook.add_format({
        'border': 1,
        'bg_color': '#FFC7CE',
        'font_color': '#9C0006',
        'align': 'center',
    })

    # Define rubric categories for columns
    rubric_categories = [
        "Etik Ilkeleri",
        "Sahne Aciklamasi",
        "Sablon Uyumu",
        "Gorsel Tasarim",
        "Zamanında Teslim",
    ]

    # Headers
    headers = ["#", "Öğrenci Adı", "Dosya Adı", "Durum", "Toplam Puan"]
    headers.extend([f"{cat} Puanı" for cat in rubric_categories])
    headers.append("Genel Değerlendirme")

    # Set column widths
    summary_sheet.set_column(0, 0, 5)   # #
    summary_sheet.set_column(1, 1, 25)  # Öğrenci Adı
    summary_sheet.set_column(2, 2, 30)  # Dosya Adı
    summary_sheet.set_column(3, 3, 10)  # Durum
    summary_sheet.set_column(4, 4, 12)  # Toplam Puan
    summary_sheet.set_column(5, 5 + len(rubric_categories) - 1, 15)  # Rubric columns
    summary_sheet.set_column(5 + len(rubric_categories), 5 + len(rubric_categories), 50)  # Genel Değerlendirme

    # Write headers
    for col, header in enumerate(headers):
        summary_sheet.write(0, col, header, header_format)

    # Write data
    for row, result in enumerate(bulk_response.results, start=1):
        summary_sheet.write(row, 0, row, cell_format)
        summary_sheet.write(row, 1, result.student_name, cell_format)
        summary_sheet.write(row, 2, result.filename, cell_format)

        if result.success:
            summary_sheet.write(row, 3, "Başarılı", success_format)
            summary_sheet.write(row, 4, result.result.total_score, cell_format)

            # Write rubric scores
            col_offset = 5
            for i, cat in enumerate(rubric_categories):
                score = 0
                for rubric in result.result.rubric_scores:
                    if rubric.category == cat:
                        score = rubric.score
                        break
                summary_sheet.write(row, col_offset + i, score, cell_format)

            # Write overall evaluation
            overall = result.result.overall_evaluation or ""
            summary_sheet.write(row, col_offset + len(rubric_categories), overall, text_format)
        else:
            summary_sheet.write(row, 3, "Hata", error_format)
            summary_sheet.write(row, 4, "-", cell_format)
            for i in range(len(rubric_categories)):
                summary_sheet.write(row, 5 + i, "-", cell_format)
            summary_sheet.write(row, 5 + len(rubric_categories), result.error or "Bilinmeyen hata", text_format)

    # Add detailed worksheet for each successful student
    for result in bulk_response.results:
        if not result.success or not result.result:
            continue

        # Clean sheet name (Excel has restrictions)
        sheet_name = re.sub(r'[\\/*?:\[\]]', '', result.student_name)[:31]
        detail_sheet = workbook.add_worksheet(sheet_name)

        detail_sheet.set_column(0, 0, 20)
        detail_sheet.set_column(1, 1, 15)
        detail_sheet.set_column(2, 2, 50)

        row = 0
        detail_sheet.write(row, 0, "Öğrenci", header_format)
        detail_sheet.write(row, 1, result.student_name, cell_format)
        row += 1

        detail_sheet.write(row, 0, "Toplam Puan", header_format)
        detail_sheet.write(row, 1, result.result.total_score, cell_format)
        row += 2

        # Rubric details
        detail_sheet.write(row, 0, "Kategori", header_format)
        detail_sheet.write(row, 1, "Puan", header_format)
        detail_sheet.write(row, 2, "Açıklama", header_format)
        row += 1

        for rubric in result.result.rubric_scores:
            detail_sheet.write(row, 0, rubric.category, cell_format)
            detail_sheet.write(row, 1, f"{rubric.score}/{rubric.max_score}", cell_format)
            detail_sheet.write(row, 2, rubric.reason, text_format)
            row += 1

        row += 1

        # Improvements
        if result.result.improvements:
            detail_sheet.write(row, 0, "İyileştirme Önerileri", header_format)
            row += 1
            for imp in result.result.improvements:
                detail_sheet.write(row, 0, imp.category, cell_format)
                detail_sheet.write(row, 1, imp.priority, cell_format)
                detail_sheet.write(row, 2, imp.suggestion, text_format)
                row += 1

    workbook.close()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=ogrenci_puanlari.xlsx"
        }
    )


@router.post("/parse", response_model=ParsedPPTX)
async def parse_only(
    file: UploadFile = File(..., description="PPTX file to parse"),
):
    """
    Parse a PPTX file and return the structured content without grading.
    Useful for debugging and testing.
    """
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Sadece .pptx dosyaları kabul edilir")

    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük")

        gate_checker = GateChecker()
        is_valid, error_msg, parsed_pptx = gate_checker.validate_file(content)

        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        return parsed_pptx

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Parse error: {e}")
        raise HTTPException(status_code=500, detail=f"Ayrıştırma hatası: {str(e)}")
