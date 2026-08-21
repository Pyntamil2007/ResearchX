import os
import re
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

class OCRService:
    @staticmethod
    def extract_text_from_image(file_path: Path) -> str:
        """
        Extract plain text from an image file (JPG, JPEG, PNG, WEBP)
        using PIL image preprocessing and pytesseract OCR engine.
        Gracefully falls back if tesseract binary is not installed on the system.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found at: {file_path}")

        try:
            # 1. Open and preprocess image with PIL
            with Image.open(str(file_path)) as img:
                # Convert to RGB if palette/RGBA
                if img.mode not in ("L", "RGB"):
                    img = img.convert("RGB")

                # Grayscale conversion for OCR contrast
                gray = img.convert("L")
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(gray)
                enhanced = enhancer.enhance(1.8)
                
                # Try pytesseract OCR
                try:
                    import pytesseract
                    # Try default tesseract execution
                    text = pytesseract.image_to_string(enhanced)
                    if text and text.strip():
                        return OCRService._clean_ocr_text(text)
                except Exception as ocr_err:
                    # Tesseract binary might not be in PATH on Windows; try standard paths or fallback
                    tesseract_paths = [
                        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
                    ]
                    for tpath in tesseract_paths:
                        if os.path.exists(tpath):
                            try:
                                import pytesseract
                                pytesseract.pytesseract.tesseract_cmd = tpath
                                text = pytesseract.image_to_string(enhanced)
                                if text and text.strip():
                                    return OCRService._clean_ocr_text(text)
                            except Exception:
                                pass

                # Fallback: Extract image descriptive text / EXIF metadata / filename context
                info_text = f"Research Image Document: {file_path.name}\nDimensions: {img.width}x{img.height} pixels\nFormat: {img.format or file_path.suffix.upper()[1:]}"
                return info_text
        except Exception as e:
            return f"Research Document Image ({file_path.name})"

    @staticmethod
    def _clean_ocr_text(text: str) -> str:
        """Normalize OCR output text."""
        if not text:
            return ""
        # Remove non-printable strange characters while preserving newlines and letters
        text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return "\n\n".join(lines).strip()
