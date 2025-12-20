# money_lines.py
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import List, Optional


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

WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class MoneyLine:
    id: int                # line index in the filtered stream
    raw_line_no: int       # line index in the original text stream
    text: str              # cleaned line text
    amount: Decimal        # extracted last $X.XX on line


def _clean_line(s: str) -> str:
    s = s.replace("\u00a0", " ")  # nbsp
    s = WHITESPACE_RE.sub(" ", s).strip()
    return s


def _parse_money_token(token: str, sign: Optional[str]) -> Optional[Decimal]:
    # token is like "1,234.56" or "1234"
    try:
        val = Decimal(token.replace(",", ""))
    except InvalidOperation:
        return None
    if sign and sign.strip() in {"-", "–", "—"}:
        val = -val
    # normalize to cents if needed
    if val == val.to_integral():
        # allow whole-dollar amounts
        return val
    return val


def extract_money_lines(text: str, *, min_abs_amount: Decimal = Decimal("0.01")) -> List[MoneyLine]:
    """
    Extract a flat list of candidate lines that contain at least one $ amount.
    We take the LAST $ amount on the line as 'amount' (matches your design).
    """
    out: List[MoneyLine] = []
    lines = text.splitlines()

    filtered_id = 0
    for raw_i, line in enumerate(lines):
        cleaned = _clean_line(line)
        if not cleaned:
            continue

        matches = list(MONEY_RE.finditer(cleaned))
        if not matches:
            continue

        last = matches[-1]
        sign = last.group("sign")
        token = last.group("num")
        amt = _parse_money_token(token, sign)
        if amt is None:
            continue
        if abs(amt) < min_abs_amount:
            continue

        out.append(MoneyLine(
            id=filtered_id,
            raw_line_no=raw_i,
            text=cleaned,
            amount=amt,
        ))
        filtered_id += 1

    return out
