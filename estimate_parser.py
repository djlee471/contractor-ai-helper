# estimate_parser.py
import json
from typing import Dict, Any
from openai import OpenAI

from estimate_parser_prompt import PARSER_SYSTEM_PROMPT
from estimate_schema import EstimateJSON


def build_parser_user_prompt(doc_role: str, filename: str, extracted_text: str) -> str:
    return f"""
You are parsing ONE document.

Return ONLY valid JSON. No markdown. No commentary.
If a value is not present, use null and add a flag.

TYPE RULES:
- confidence fields must be numbers between 0 and 1 (e.g., 0.8). Never "high", "medium", or "low".
- provenance must be either an object {{page, method}} or null. Never "".
- Do not include raw text excerpts from the PDF.
- Do not include snippet or source_ref fields anywhere.
- If unknown, use null (not "", not "unknown").
- Do not add any keys not listed (including inside nested objects).

doc_role: {doc_role}
file_name: {filename}

LINE ITEMS LIMIT (CRITICAL):
- Extract at most 20 line_items total.
- If the document contains more line items than you extracted, set:
  source.has_more_line_items = true
  source.line_items_extracted = <number extracted>
- Then STOP adding line items and finish the JSON (close all braces).

Fill this schema (no extra keys):
- schema_version: "1.0.0"
- source: object including at least:
  - doc_role: "{doc_role}"
  - file_name: "{filename}"
  - has_more_line_items: true/false or null
  - line_items_extracted: number or null
- format_family: "xactimate_like" or "freeform" or "unknown"
- line_items: list of objects with:
  - id (string, create stable ids like "LI-0001")
  - area (string or null)
  - category (string or null)
  - description: {{ text, trade_code }}   # DO NOT include raw
  - quantity: {{ value, unit, raw_qty, raw_unit, confidence, provenance }}
  - unit_price: {{ value, confidence, provenance }}
  - components: dict of Money objects (keys like "material","labor","equipment" if present)
  - line_total: Money
  - flags: list of strings
  - provenance: {{ page, method }}

Note:
- quantity.provenance and unit_price.provenance follow the same structure: {{ page, method }} or null

PRIORITY ORDER:
1) source, schema_version, format_family
2) line_items (up to the limit)
3) document_totals
4) all remaining fields may be empty or default if needed to keep JSON valid

document_totals: extract stated totals if present (subtotal, tax, overhead_profit, rcv_total, acv_total, net_claim)
computed_totals: leave as defaults/zeros; do NOT compute
reconciliation: leave empty
assumptions_exclusions: list of strings (if present)
open_questions: list of strings (if uncertainties)

EXTRACTED TEXT (may be messy):
<<<
{extracted_text}
>>>
""".strip()

def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        # remove ```json or ``` and ending ```
        s = s.split("```", 1)[1]
        if s.strip().lower().startswith("json"):
            s = s.strip()[4:].strip()
        if s.endswith("```"):
            s = s.rsplit("```", 1)[0]
    return s.strip()


def extract_first_json_object(text: str) -> str:
    """
    Extract the first complete top-level JSON object {...} from text using brace matching.
    Ignores braces inside JSON strings.
    """
    in_str = False
    esc = False
    depth = 0
    start = None

    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start is not None:
                        return text[start:i + 1]

    raise ValueError("No complete top-level JSON object found in model output.")


def prune_brittle_fields(obj):
    """
    Deterministically remove fields most likely to break JSON (snippets/raw).
    Safe even if they don't exist.
    """
    if isinstance(obj, dict):
        obj.pop("snippet", None)
        obj.pop("raw", None)
        obj.pop("currency", None)
        for k, v in list(obj.items()):
            obj[k] = prune_brittle_fields(v)
        return obj
    if isinstance(obj, list):
        return [prune_brittle_fields(x) for x in obj]
    return obj

def normalize_estimate_json_types(data: dict) -> dict:
    CONF_MAP = {"high": 0.9, "medium": 0.6, "low": 0.3}

    def walk(x):
        if isinstance(x, dict):
            out = {}
            for k, v in x.items():

                # Empty string -> null
                if v == "":
                    v = None

                # Ensure Description.text is always a string
                if k == "text" and v is None:
                    v = ""

                # Confidence normalization
                if k == "confidence":
                    if isinstance(v, str):
                        vv = v.strip().lower()
                        if vv in CONF_MAP:
                            v = CONF_MAP[vv]
                        else:
                            try:
                                v = float(vv)
                            except Exception:
                                v = None
                    elif isinstance(v, (int, float)):
                        v = max(0.0, min(1.0, float(v)))
                    else:
                        v = None

                # Provenance normalization
                if k == "provenance":
                    if v is None:
                        v = None
                    elif isinstance(v, str):
                        # sometimes model puts method string here
                        v = {"page": None, "method": v}

                out[k] = walk(v)
            return out

        if isinstance(x, list):
            return [walk(i) for i in x]

        return x

    return walk(data)

def parse_estimate_doc(
    client: OpenAI,
    *,
    doc_role: str,
    filename: str,
    extracted_text: str,
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    """
    Parse ONE estimate document into validated JSON (dict).
    LLM structures; Python validates. No math here.
    """
    user_prompt = build_parser_user_prompt(doc_role, filename, extracted_text)

    resp = client.responses.create(
        model=model,
        instructions=PARSER_SYSTEM_PROMPT,
        input=user_prompt,
        max_output_tokens=12000,
        temperature=0.0,
        store=False,
    )

    raw_text = _strip_code_fences(resp.output_text)
    print("MAIN OUTPUT LENGTH:", len(raw_text))
    used_repair = False

    # First attempt: extract first JSON object and parse
    try:
        if not raw_text.lstrip().startswith("{"):
            print("DIRECT OUTPUT DOES NOT START WITH '{' (first 200 chars):")
            print(raw_text[:200])

        raw_json = extract_first_json_object(raw_text)
        data = json.loads(raw_json)

    except Exception as e:
        print("DIRECT PARSE FAILED:", repr(e))
        print("DIRECT OUTPUT (first 400 chars):")
        print(raw_text[:400])

        used_repair = True

        # Repair pass (only if first attempt fails)
        repair_instructions = (
            "You fix malformed JSON and return ONLY valid JSON.\n"
            "Rules:\n"
            "- Output must be a single JSON object.\n"
            "- Use double quotes for all keys and string values.\n"
            "- Use only JSON primitives: null, true, false, numbers, strings, arrays, objects.\n"
            "- NEVER output NaN, Infinity, -Infinity, None.\n"
            "- If a numeric value is unknown, use null.\n"
            "- Escape internal quotes as \\\" and newlines as \\n.\n"
            "- If a string value is causing issues, shorten it aggressively or replace with \"\".\n"
            "- Do not add new keys (do not invent fields).\n"
            "- No trailing commas.\n"
            "- Provenance may include only keys: page, method. Do not include snippet or source_ref.\n"
        )

        repair_input = f"""
Return ONLY a single valid JSON object.

If the content is too long, shorten string values aggressively.
Do not include any raw text excerpts.

CONTENT TO FIX:
<<<
{raw_text[:12000]}
>>>
""".strip()

        repair_resp = client.responses.create(
            model="gpt-4o-mini",
            instructions=repair_instructions,
            input=repair_input,
            max_output_tokens=6000,
            temperature=0.0,
            store=False,
        )

        fixed_text = _strip_code_fences(repair_resp.output_text)

        # DEBUG: inspect repair output BEFORE JSON extraction
        print("---- REPAIR OUTPUT (first 800 chars) ----")
        print(fixed_text[:800])
        print("---- REPAIR OUTPUT (last 400 chars) ----")
        print(fixed_text[-400:])

        try:
            fixed_json = extract_first_json_object(fixed_text)
            data = json.loads(fixed_json)
        except json.JSONDecodeError as e:
            # Your debug prints (kept), but now always defined
            print("---- JSON REPAIR OUTPUT (first 1200 chars) ----")
            print(fixed_text[:1200])
            print("---- JSON REPAIR OUTPUT (last 800 chars) ----")
            print(fixed_text[-800:])
            print("---- JSONDecodeError ----")
            print("msg:", e.msg)
            print("line:", e.lineno, "col:", e.colno, "pos:", e.pos)

            lines = fixed_text.splitlines()
            start = max(e.lineno - 3, 1)
            end = min(e.lineno + 3, len(lines))
            print(f"---- Context lines {start}..{end} ----")
            for i in range(start, end + 1):
                print(f"{i:04d}: {lines[i-1]}")

            raise

    # Deterministic cleanup so validation isn't held hostage by long/raw/snippet fields
    data = prune_brittle_fields(data)
    data = normalize_estimate_json_types(data)

    print("PARSE PATH:", "REPAIR" if used_repair else "DIRECT")
    print("LINE ITEMS:", len(data.get("line_items", [])))
    print("FORMAT FAMILY:", data.get("format_family"))

    data.setdefault("source", {})
    data["source"]["doc_role"] = doc_role
    data["source"]["file_name"] = filename

    if not isinstance(data.get("reconciliation"), list):
        data["reconciliation"] = []
        
    # optional but recommended: guard other list fields
    for k in ["assumptions_exclusions", "open_questions", "line_items"]:
        if not isinstance(data.get(k), list):
            data[k] = []

    validated = EstimateJSON.model_validate(data)
    return validated.model_dump()
