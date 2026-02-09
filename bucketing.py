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
        "You are classifying construction estimate line-items into cost buckets.\n\n"
        "DEFINITIONS (IMPORTANT):\n"
        "- Each bucket represents a TRADE or MATERIAL SCOPE.\n"
        "- Include ONLY:\n"
        "  1) the core material or task itself, AND\n"
        "  2) materials and labor REQUIRED to install or complete that task.\n"
        "- Exclude:\n"
        "  - fixtures, enclosures, appliances, cabinetry, glazing, or specialty items that are a SEPARATE TRADE,\n"
        "    even if they appear nearby or in the same room.\n\n"
        "SCOPE BOUNDARY EXAMPLES:\n"
        "- TILE includes tile surface work and required install components\n"
        "  (substrate, setting materials, waterproofing, grout/sealer).\n"
        "- TILE does NOT include separate-trade items whose primary purpose is fixtures,\n"
        "  enclosures, cabinetry, glazing, plumbing, or electrical.\n\n"
        "- FLOORING HARD (WOOD) includes flooring material, finishing, and required prep/underlayment.\n"
        "- FLOORING HARD (WOOD) does NOT include unrelated finish carpentry, door work,\n"
        "  or other separate trades not required to install the flooring itself.\n\n"
        "RULES:\n"
        "- Choose EXACTLY ONE bucket for each item.\n"
        "- Allowed buckets (no others):\n"
        f"{BUCKETS}\n"
        "- Do NOT do any math.\n"
        "- Do NOT add or remove items.\n"
        "- If an item represents a separate trade or is not required to install the material,\n"
        "  choose 'other'.\n\n"
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

    # DEBUG 12/22
    system_msg = "You follow instructions exactly and output only strict JSON."
    prompt_chars = len(system_msg) + len(prompt)
    print("[DEBUG] BUCKETING total prompt chars:", prompt_chars)

    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "You follow instructions exactly and output only strict JSON."},
            {"role": "user", "content": prompt},
        ],
  #      response_format={"type": "json_object"}, # speeds up bucketing by ignoring
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
