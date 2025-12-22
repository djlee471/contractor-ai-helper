# material_totals.py
from __future__ import annotations

from typing import Dict, Any
from decimal import Decimal

from money_lines import extract_atomic_money_lines
from bucketing import bucket_money_lines
from summation import sum_by_bucket
from buckets import BUCKETS
import time

def compute_material_totals(
    *,
    client,
    model: str,
    extracted_text: str,
    min_abs_amount: Decimal = Decimal("0.01"),
) -> Dict[str, Any]:

    # ----------------------------
    # Atomic extraction timing
    # ----------------------------
    t0 = time.perf_counter()  # time debug
    money_lines = extract_atomic_money_lines(
        extracted_text,
        min_abs_amount=min_abs_amount,
    )
    t1 = time.perf_counter()  # time debug
    atomic_time = t1 - t0     # time debug
    print("[DEBUG] BUCKETING money_lines count:", len(money_lines))

    print(
        f"[TIMING] atomic extraction: {atomic_time:.2f}s "
        f"({len(money_lines)} lines)"
    )  # time debug

    # ----------------------------
    # Bucketing LLM timing
    # ----------------------------
    t0 = time.perf_counter()  # time debug
    bucket_map = bucket_money_lines(
        client,
        model,
        money_lines,
    )
    t1 = time.perf_counter()  # time debug
    bucket_time = t1 - t0     # time debug

    print(
        f"[TIMING] bucketing LLM call: {bucket_time:.2f}s"
    )  # time debug

    # ----------------------------
    # Deterministic aggregation
    # ----------------------------
    totals, grouped = sum_by_bucket(money_lines, bucket_map)

    # Order totals by BUCKETS list and drop empties
    ordered = []
    for b in BUCKETS:
        amt = totals.get(b, Decimal("0.00"))
        if amt != Decimal("0.00"):
            ordered.append((b, amt))

    # ----------------------------
    # Return results + timings
    # ----------------------------
    return {
        "money_lines": money_lines,          # for debugging UI
        "bucket_map": bucket_map,
        "totals_ordered": ordered,           # list[(bucket, Decimal)]
        "grouped": grouped,                  # bucket -> [MoneyLine]
        "timings": {                         # time debug
            "atomic_extraction_s": atomic_time,
            "bucketing_llm_s": bucket_time,
        },
    }
