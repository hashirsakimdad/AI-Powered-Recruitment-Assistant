import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import docx2txt
import fitz  # PyMuPDF

# Optional OCR imports (fallback if text extraction fails)
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    convert_from_path = None


def extract_text(file_path: str, use_ocr_fallback: bool = True) -> str:
    """
    Extract text from PDF or DOCX file.
    For PDFs: Uses PyMuPDF first, falls back to OCR if text extraction fails.
    
    Args:
        file_path: Path to the file
        use_ocr_fallback: Whether to use OCR if text extraction fails
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If file type is unsupported or extraction fails
    """
    path = Path(file_path)
    
    if path.suffix.lower() == ".pdf":
        # Try PyMuPDF first (faster, more accurate for text-based PDFs)
        try:
            with fitz.open(file_path) as doc:
                text = "\n".join(page.get_text() for page in doc)
                
                # Check if text extraction was successful (not empty or too short)
                if text and len(text.strip()) > 50:
                    return text
                
                # If text is too short or empty, might be scanned PDF - try OCR
                if use_ocr_fallback and OCR_AVAILABLE:
                    return _extract_text_with_ocr(file_path)
                elif not text or len(text.strip()) < 50:
                    raise ValueError(
                        "Could not extract sufficient text from PDF. "
                        "The file may be a scanned image. OCR support requires pytesseract and pdf2image."
                    )
                return text
        except Exception as e:
            # If PyMuPDF fails, try OCR if available
            if use_ocr_fallback and OCR_AVAILABLE:
                try:
                    return _extract_text_with_ocr(file_path)
                except Exception as ocr_error:
                    raise ValueError(
                        f"Failed to extract text from PDF: {str(e)}. "
                        f"OCR also failed: {str(ocr_error)}"
                    )
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    elif path.suffix.lower() == ".docx":
        try:
            text = docx2txt.process(file_path) or ""
            if not text or len(text.strip()) < 10:
                raise ValueError("Could not extract text from DOCX file. File may be corrupted or empty.")
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")


def _extract_text_with_ocr(file_path: str) -> str:
    """
    Extract text from PDF using OCR (Tesseract).
    Used as fallback when PyMuPDF cannot extract text (e.g., scanned PDFs).
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text from OCR
        
    Raises:
        ValueError: If OCR fails or is not available
    """
    if not OCR_AVAILABLE:
        raise ValueError("OCR support not available. Install pytesseract and pdf2image.")
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path, dpi=300)
        
        # Extract text from each image using OCR
        text_parts = []
        for image in images:
            text = pytesseract.image_to_string(image)
            text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        
        if not full_text or len(full_text.strip()) < 50:
            raise ValueError("OCR extracted insufficient text. File may be corrupted or unreadable.")
        
        return full_text
    except Exception as e:
        raise ValueError(f"OCR extraction failed: {str(e)}")


def _regex_capture(pattern: str, text: str) -> List[str]:
    matches = re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return [m.strip() for m in matches if m]


def parse_resume(text: str) -> Dict[str, List[str] | str]:
    skills = _regex_capture(r"skills?:\s*(.*)", text)
    education = _regex_capture(r"(bachelor|master|ph\.d|bs|ms)[^,\n]*", text)
    experiences = _regex_capture(
        r"(developer|engineer|analyst|manager)[^,\n]*", text
    )
    years_exp = _estimate_years_experience(text)
    return {
        "skills": skills,
        "education": education,
        "experiences": experiences,
        "years_experience": years_exp,
        "raw_text": text[:2000],
    }


def _estimate_years_experience(text: str) -> float:
    # Find patterns like "5 years", "3+ years", etc.
    import re
    pattern = r"(\d+)\s*\+?\s*(?:years?|yrs?)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    values = []
    for match in matches:
        try:
            # match is a tuple from findall, get first element
            if isinstance(match, tuple):
                values.append(float(match[0]))
            else:
                values.append(float(match))
        except (ValueError, IndexError, TypeError):
            continue
    return float(max(values)) if values else 0.0

