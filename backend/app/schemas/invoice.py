"""
Invoice schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


class InvoiceCreate(BaseModel):
    """Schema for invoice creation request."""
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date
    supplier_gstin: str = Field(..., min_length=15, max_length=15)
    supplier_name: str
    recipient_gstin: str = Field(..., min_length=15, max_length=15)
    recipient_name: str
    taxable_value: float = Field(..., gt=0)
    igst: float = Field(default=0.0, ge=0)
    cgst: float = Field(default=0.0, ge=0)
    sgst: float = Field(default=0.0, ge=0)
    total_value: float = Field(..., gt=0)
    hsn_code: Optional[str] = Field(None, min_length=4, max_length=8)
    place_of_supply: str = Field(..., min_length=2, max_length=2)


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""
    id: int
    company_id: int
    invoice_number: str
    invoice_date: date
    supplier_gstin: str
    supplier_name: str
    recipient_gstin: str
    recipient_name: str
    taxable_value: float
    igst: float
    cgst: float
    sgst: float
    total_value: float
    hsn_code: Optional[str]
    place_of_supply: str
    is_duplicate: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceUploadResponse(BaseModel):
    """Schema for invoice upload response."""
    success: bool
    message: str
    invoice_count: int
    total_value: float
    duplicate_count: int = 0
    errors: List[dict] = []
