# bucketing.py
from __future__ import annotations

import json
from typing import Dict, List, Any

from buckets import BUCKETS, BUCKET_SET
from money_lines import MoneyLine


def _build_bucketing_prompt(money_lines: List[MoneyLine]) -> str:
    # Keep payload small: id, amount, text
    items = [{"id": ml.id, "amount": str(ml.amount), "text": ml.text} for ml in money_lines]

    return (
        "You are classifying insurance estimate line-items into cost buckets.\n"
        "RULES:\n"
        "- Choose EXACTLY ONE bucket for each item.\n"
        "- Allowed buckets (no others):\n"
        f"{BUCKETS}\n"
        "- Do NOT do any math.\n"
        "- Do NOT add or remove items.\n"
        "- If unsure, choose 'other'.\n\n"
        "Return ONLY valid JSON with this exact shape:\n"
        "{\n"
        '  "assignments": [\n'
        '    {"id": 0, "bucket": "flooring_carpet"},\n'
        '    ...\n'
        "  ]\n"
        "}\n\n"
        "ITEMS:\n"
        f"{json.dumps(items, ensure_ascii=False)}"
    )


def bucket_money_lines(client, model: str, money_lines: List[MoneyLine]) -> Dict[int, str]:
    """
    Returns mapping: {money_line_id: bucket}
    """
    prompt = _build_bucketing_prompt(money_lines)

    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "You follow instructions exactly and output only strict JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    data = json.loads(raw)

    assignments = data.get("assignments", [])
    mapping: Dict[int, str] = {}
    for a in assignments:
        try:
            _id = int(a["id"])
            bucket = str(a["bucket"])
        except Exception:
            continue
        if bucket not in BUCKET_SET:
            bucket = "other"
        mapping[_id] = bucket

    # Ensure every money line has a bucket (default other)
    for ml in money_lines:
        mapping.setdefault(ml.id, "other")

    return mapping
