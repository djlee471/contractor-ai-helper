# buckets.py
from __future__ import annotations

BUCKETS = [
    # Interior work
    "demo",
    "drywall",
    "painting_interior",
    "flooring_carpet",
    "flooring_hard",
    "tile",
    "trim_finish",
    "doors_windows",
    "cabinets_countertops",
    "plumbing",
    "electrical",
    "hvac",
    "insulation",
    "appliances",
    "contents",

    # Exterior work
    "exterior_roofing",
    "exterior_siding",
    "exterior_painting",
    "exterior_windows_doors",
    "exterior_fencing",
    "exterior_concrete_flatwork",
    "landscaping",

    # Temporary / pre-repair
    "mitigation",
    "equipment_rentals",
    "temporary_services",

    # Financial / administrative
    "taxes",
    "overhead_profit",
    "insurance_financials",

    # Catch-all
    "other",
]

BUCKET_SET = set(BUCKETS)
