# money_lines.py
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import List, Optional


# Matches dollar amounts like "$1,234.56"
MONEY_RE = re.compile(
    r"""
    (?P<sign>[-–—])?\s*          # optional minus-like sign
    \$\s*
    (?P<num>
        (?:\d{1,3}(?:,\d{3})*|\d+)   # 1,234 or 1234
        (?:\.\d{2})?                 # optional .00
    )
    """,
    re.VERBOSE,
)

# Matches numbered line items like "27. Carpet ..."
LINE_ITEM_RE = re.compile(r"^\s*\d+\.\s+")

# Matches plain money-like numbers without "$", e.g. "1,166.14"
NUM_MONEY_RE = re.compile(r"\b\d{1,3}(?:,\d{3})*\.\d{2}\b")

WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class MoneyLine:
    id: int                # line index in the filtered stream
    raw_line_no: int       # line index in the original text stream
    text: str              # cleaned line text
    amount: Decimal        # extracted line-item or $ amount


def _clean_line(s: str) -> str:
    s = s.replace("\u00a0", " ")  # nbsp
    s = WHITESPACE_RE.sub(" ", s).strip()
    return s


def _parse_money_token(token: str, sign: Optional[str]) -> Optional[Decimal]:
    try:
        val = Decimal(token.replace(",", ""))
    except InvalidOperation:
        return None

    if sign and sign.strip() in {"-", "–", "—"}:
        val = -val

    return val


def extract_money_lines(
    text: str,
    *,
    min_abs_amount: Decimal = Decimal("0.01"),
) -> List[MoneyLine]:
    """
    Extract candidate money lines.

    Supports:
    1) Numbered line items where the RCV appears as a plain number
       (e.g. "27. Carpet ... 1,166.14")
    2) Lines with explicit $ amounts (summary / financial lines)

    Preference is given to numbered line items.
    """
    out: List[MoneyLine] = []
    lines = text.splitlines()
    filtered_id = 0

    for raw_i, line in enumerate(lines):
        cleaned = _clean_line(line)
        if not cleaned:
            continue

        amt: Optional[Decimal] = None

        # --- Path 1: numbered line items (preferred) ---
        if LINE_ITEM_RE.match(cleaned):
            nums = NUM_MONEY_RE.findall(cleaned)
            if nums:
                token = nums[-1]  # last numeric column = line total (RCV)
                amt = _parse_money_token(token, sign=None)

        # --- Path 2: explicit $ amounts (fallback) ---
        if amt is None:
            matches = list(MONEY_RE.finditer(cleaned))
            if matches:
                last = matches[-1]
                sign = last.group("sign")
                token = last.group("num")
                amt = _parse_money_token(token, sign)

        if amt is None:
            continue
        if abs(amt) < min_abs_amount:
            continue

        out.append(
            MoneyLine(
                id=filtered_id,
                raw_line_no=raw_i,
                text=cleaned,
                amount=amt,
            )
        )
        filtered_id += 1

    return out
