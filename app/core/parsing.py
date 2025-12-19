import os
from pathlib import Path
from pypdf import PdfReader


def parse_document(file_path: str) -> str:
    """
    Parse a document and extract text content.
    Supports PDF and TXT files.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return _parse_pdf(file_path)
    elif extension == ".txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def _parse_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)


def _parse_txt(file_path: str) -> str:
    """Read text from TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
