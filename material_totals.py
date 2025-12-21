# material_totals.py
from __future__ import annotations

from typing import Dict, Any
from decimal import Decimal

from money_lines import extract_atomic_money_lines
from bucketing import bucket_money_lines
from summation import sum_by_bucket
from buckets import BUCKETS


def compute_material_totals(
    *,
    client,
    model: str,
    extracted_text: str,
    min_abs_amount: Decimal = Decimal("0.01"),
) -> Dict[str, Any]:
    money_lines = extract_atomic_money_lines(extracted_text, min_abs_amount=min_abs_amount)
    bucket_map = bucket_money_lines(client, model, money_lines)
    totals, grouped = sum_by_bucket(money_lines, bucket_map)

    # Order totals by BUCKETS list and drop empties
    ordered = []
    for b in BUCKETS:
        amt = totals.get(b, Decimal("0.00"))
        if amt != Decimal("0.00"):
            ordered.append((b, amt))

    return {
        "money_lines": money_lines,      # for debugging UI
        "bucket_map": bucket_map,
        "totals_ordered": ordered,       # list[(bucket, Decimal)]
        "grouped": grouped,              # bucket -> [MoneyLine]
    }
