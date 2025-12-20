# summation.py
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Tuple

from money_lines import MoneyLine


def sum_by_bucket(
    money_lines: List[MoneyLine],
    bucket_map: Dict[int, str],
) -> Tuple[Dict[str, Decimal], Dict[str, List[MoneyLine]]]:
    totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    grouped: Dict[str, List[MoneyLine]] = defaultdict(list)

    for ml in money_lines:
        b = bucket_map.get(ml.id, "other")
        grouped[b].append(ml)
        totals[b] += ml.amount

    # cast back to normal dicts
    return dict(totals), dict(grouped)
