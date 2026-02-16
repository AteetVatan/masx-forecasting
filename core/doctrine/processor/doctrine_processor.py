import logging
import re
from pathlib import Path

from core.config.paths import Paths
from core.domain.constants import SUPPORTED_DOC_EXTENSIONS
from core.domain.exceptions import FileProcessingError
from core.doctrine.text_splitter import split_text

logger = logging.getLogger(__name__)

_SLUG_PATTERN = re.compile(r"[^a-zA-Z0-9]+")


class DoctrineProcessor:
    @staticmethod
    def batch_process() -> None:
        _process_text_files()
        _process_pdf_files()

    @staticmethod
    def extract_slug(filename: str) -> str:
        name = Path(filename).stem
        return _SLUG_PATTERN.sub("_", name).strip("_").lower()


def _process_text_files() -> None:
    txt_files = list(Paths.RAW_DIR.glob("*.txt"))
    for file_path in txt_files:
        slug = DoctrineProcessor.extract_slug(file_path.name)
        cleaned_path = Paths.CLEANED_DIR / f"{slug}.md"
        if cleaned_path.exists():
            logger.info("Skipping %s — already cleaned", slug)
            continue
        _clean_and_save_text(file_path, cleaned_path)


def _process_pdf_files() -> None:
    try:
        import fitz
        import easyocr
    except ImportError:
        logger.warning("PyMuPDF or EasyOCR not installed — skipping PDF processing")
        return

    pdf_files = list(Paths.RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        return

    reader = easyocr.Reader(["en"])
    for file_path in pdf_files:
        slug = DoctrineProcessor.extract_slug(file_path.name)
        cleaned_path = Paths.CLEANED_DIR / f"{slug}.md"
        if cleaned_path.exists():
            continue
        _extract_pdf_text(file_path, cleaned_path, reader)


def _clean_and_save_text(source: Path, dest: Path) -> None:
    try:
        raw = source.read_text(encoding="utf-8")
        cleaned = _clean_text(raw)
        dest.write_text(cleaned, encoding="utf-8")
        logger.info("Cleaned %s → %s", source.name, dest.name)
    except Exception as e:
        raise FileProcessingError(f"Failed to clean {source}: {e}") from e


def _extract_pdf_text(pdf_path: Path, dest: Path, reader) -> None:
    import fitz

    try:
        doc = fitz.open(str(pdf_path))
        all_text: list[str] = []
        for page in doc:
            text = page.get_text()
            if text.strip():
                all_text.append(text)
            else:
                all_text.append(_ocr_page(page, reader))
        doc.close()

        cleaned = _clean_text("\n".join(all_text))
        dest.write_text(cleaned, encoding="utf-8")
        logger.info("Extracted PDF %s → %s", pdf_path.name, dest.name)
    except Exception as e:
        raise FileProcessingError(f"Failed to process PDF {pdf_path}: {e}") from e


def _ocr_page(page, reader) -> str:
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    results = reader.readtext(img_bytes)
    return " ".join(text for _, text, _ in results)


def _clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()
