# estimate_extract.py
from typing import List, Dict, Any
from io import BytesIO
import pdfplumber

import re


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


# ── Pass A: labeled-field redaction ──────────────────────────────────────────

_LABEL_RE = re.compile(
    r"""
    ^(                          # start of line
        [ \t]*                  # optional leading whitespace
        (?:
            Insured | Client | Property | Loss\s*Location |
            Claim(?:\s*Number)? | Policy(?:\s*Number)? |
            Estimate(?:\s*(?:ID|Number|#))? |
            Home | Cell(?:ular)? | Phone | Mobile |
            E[\-\s]?mail | Email |
            Adjuster | Estimator | Inspector | Operator |
            Date\s*of\s*Loss | Date\s*Inspected
        )
        [ \t]*:[ \t]*           # colon + optional space
    )
    (.+)$                       # the value to redact
    """,
    re.IGNORECASE | re.VERBOSE | re.MULTILINE,
)

# ── Pass B: global pattern cleanup ───────────────────────────────────────────

_EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)

_PHONE_RE = re.compile(
    r"""
    (?:\+?1[\s\-.])?            # optional country code
    \(?\d{3}\)?                 # area code
    [\s\-.]                     # separator
    \d{3}                       # exchange
    [\s\-.]                     # separator
    \d{4}                       # number
    (?:[ \t]*(?:x|ext)\.?[ \t]*\d+)?  # optional extension (handles long ext too)
    """,
    re.VERBOSE,
)

_CLAIM_INLINE_RE = re.compile(
    r"(?:claim|policy|estimate)[\s#:]*([A-Z0-9\-]{6,})",
    re.IGNORECASE,
)

# ── Running page header ───────────────────────────────────────────────────────
# Xactimate puts "LAST, FIRST  CLAIM#" on the first line of most pages.
# We detect this by looking for the claim number (extracted from Pass A)
# and removing any line that contains it outside of labeled fields.

def _strip_running_headers(text: str, claim_number: str) -> str:
    """Remove page-header lines that contain the bare claim number."""
    if not claim_number:
        return text
    escaped = re.escape(claim_number)
    pattern = re.compile(
        r"^[^\n]*" + escaped + r"[^\n]*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return pattern.sub("[HEADER REDACTED]", text)


def redact_estimate_text(text: str) -> str:
    """
    Two-pass PII redaction on extracted estimate text.
    Returns redacted text; labels are preserved, values replaced with [REDACTED].
    """
    if not text:
        return text

    # ── Capture claim number before redacting (needed for header stripping) ──
    claim_match = re.search(
        r"(?:Claim(?:\s*Number)?)\s*:?\s*([A-Z0-9\-]{6,})",
        text,
        re.IGNORECASE,
    )
    claim_number = claim_match.group(1).strip() if claim_match else ""

    # ── Pass A: label-based line redaction ───────────────────────────────────
    redacted = _LABEL_RE.sub(lambda m: m.group(1) + "[REDACTED]", text)

    # ── Strip running page headers (Xactimate header rows) ───────────────────
    if claim_number:
        redacted = _strip_running_headers(redacted, claim_number)

    # ── Pass B: global pattern sweep ─────────────────────────────────────────
    redacted = _EMAIL_RE.sub("[REDACTED]", redacted)
    redacted = _PHONE_RE.sub("[REDACTED]", redacted)
    redacted = _CLAIM_INLINE_RE.sub(
        lambda m: m.group(0).replace(m.group(1), "[REDACTED]"),
        redacted,
    )

    return redacted


def extract_pdf_pages_text(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    packets: List[Dict[str, Any]] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            packets.append({"page": i, "text": text, "method": "pdfplumber"})
    return packets


def join_page_packets(packets: List[Dict[str, Any]]) -> str:
    parts = []
    for p in packets:
        parts.append(f"\n--- PAGE {p['page']} ---\n{p['text']}".rstrip())
    return "\n".join(parts).strip()