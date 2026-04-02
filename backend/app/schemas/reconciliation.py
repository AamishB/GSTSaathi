"""
Reconciliation schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


class ReconciliationResultSchema(BaseModel):
    """Schema for reconciliation result."""
    id: int
    invoice_id: int
    invoice_number: str
    supplier_gstin: str
    invoice_date: date
    taxable_value: float
    match_status: str  # matched, missing_in_gstr2b, value_mismatch, gstin_error, timing_diff
    match_confidence: str  # exact, partial, no_match
    taxable_value_diff: Optional[float] = None
    tax_value_diff: Optional[float] = None
    mismatch_category: Optional[str] = None
    action_taken: str  # pending, resolved, reversed
    reconciled_at: datetime
    
    class Config:
        from_attributes = True


class ReconciliationRunRequest(BaseModel):
    """Schema for reconciliation run request."""
    pass  # No body required, uses uploaded data


class ReconciliationRunResponse(BaseModel):
    """Schema for reconciliation run response."""
    status: str  # running, completed, failed
    job_id: str
    message: str


class ReconciliationStatusResponse(BaseModel):
    """Schema for reconciliation status response."""
    status: str
    job_id: str
    matched_count: int
    mismatch_count: int
    itc_eligible: float
    itc_at_risk: float
    completed_at: Optional[datetime] = None


class ReconciliationResultsResponse(BaseModel):
    """Schema for reconciliation results list response."""
    results: List[ReconciliationResultSchema]
    total: int
    matched_count: int
    mismatch_count: int


class ReconciliationLogItem(BaseModel):
    """Schema for a reconciliation run log record."""
    id: int
    job_id: str
    matched_count: int
    mismatch_count: int
    itc_at_risk: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReconciliationLogResponse(BaseModel):
    """Schema for reconciliation log list response."""
    logs: List[ReconciliationLogItem]
    total: int


class WhatsAppReminderRequest(BaseModel):
    """Schema for triggering WhatsApp reminders to vendors."""
    vendor_gstins: List[str] = Field(default_factory=list)
    language: str = Field(default="hi", pattern="^(hi|en)$")


class WhatsAppReminderResult(BaseModel):
    """Per-vendor WhatsApp send result."""
    vendor_gstin: str
    sent: bool
    timestamp: str


class WhatsAppReminderResponse(BaseModel):
    """Schema for WhatsApp reminder summary response."""
    status: str
    total_candidates: int
    reminders_generated: int
    reminders_sent: int
    language: str
    results: List[WhatsAppReminderResult]
    message: str


class MismatchRecord(BaseModel):
    """Schema for mismatch record in reports."""
    invoice_number: str
    invoice_date: date
    supplier_gstin: str
    supplier_name: str
    booked_taxable_value: float
    gstr2b_taxable_value: Optional[float]
    tax_difference: float
    mismatch_type: str
    action_taken: str
