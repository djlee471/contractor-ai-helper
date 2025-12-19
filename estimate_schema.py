from __future__ import annotations
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, conlist

DocRole = Literal["insurance", "contractor"]
FormatFamily = Literal["xactimate_like", "freeform", "unknown"]
Currency = Literal["USD"]

class Source(BaseModel):
    doc_role: DocRole
    file_name: str

    # optional / hardening fields
    has_more_line_items: Optional[bool] = None
    line_items_extracted: Optional[int] = None

class Provenance(BaseModel):
    page: Optional[int] = None
    method: Optional[str] = None

class Money(BaseModel):
    value: Optional[float] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    provenance: Optional[Provenance] = None

class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_qty: Optional[str] = None
    raw_unit: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    provenance: Optional[Provenance] = None

class Description(BaseModel):
    text: str
    trade_code: Optional[str] = None

class LineItem(BaseModel):
    id: str
    area: Optional[str] = None
    category: Optional[str] = None

    description: Description
    quantity: Optional[Quantity] = None
    unit_price: Optional[Money] = None

    components: Dict[str, Money] = Field(default_factory=dict)  # material/labor/etc
    line_total: Money = Field(default_factory=Money)

    flags: List[str] = Field(default_factory=list)
    provenance: Optional[Provenance] = None

class DocumentTotals(BaseModel):
    subtotal: Optional[Money] = None
    tax: Optional[Money] = None
    overhead_profit: Optional[Money] = None
    rcv_total: Optional[Money] = None
    acv_total: Optional[Money] = None
    net_claim: Optional[Money] = None

class ComputedTotals(BaseModel):
    line_items_subtotal: float = 0.0
    by_bucket: Dict[str, float] = Field(default_factory=lambda: {
        "materials": 0.0, "labor": 0.0, "equipment": 0.0, "subcontract": 0.0, "other": 0.0
    })

class ReconciliationCheck(BaseModel):
    check_id: str
    severity: Literal["info", "warning", "fail"]
    document_value: Optional[float] = None
    computed_value: Optional[float] = None
    delta: Optional[float] = None
    notes: Optional[str] = None

class EstimateJSON(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0.0"
    source: Source

    format_family: FormatFamily = "unknown"

    line_items: List[LineItem] = Field(default_factory=list)

    document_totals: DocumentTotals = Field(default_factory=DocumentTotals)
    computed_totals: ComputedTotals = Field(default_factory=ComputedTotals)

    reconciliation: List[ReconciliationCheck] = Field(default_factory=list)

    assumptions_exclusions: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
