# estimate_extract.py
from typing import List, Dict, Any
from io import BytesIO
import pdfplumber

def extract_pdf_pages_text(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Returns a list of page packets:
      [{ "page": 1, "text": "...", "method": "pdfplumber" }, ...]
    """
    packets: List[Dict[str, Any]] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            packets.append({"page": i, "text": text, "method": "pdfplumber"})
    return packets

def join_page_packets(packets: List[Dict[str, Any]]) -> str:
    """
    Makes a single string for the LLM.
    """
    parts = []
    for p in packets:
        parts.append(f"\n--- PAGE {p['page']} ---\n{p['text']}".rstrip())
    return "\n".join(parts).strip()