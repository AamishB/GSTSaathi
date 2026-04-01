"""
Company schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CompanyCreate(BaseModel):
    """Schema for company creation request."""
    gstin: str = Field(..., min_length=15, max_length=15, description="15-character GSTIN")
    legal_name: str = Field(..., min_length=1, max_length=255)
    trade_name: Optional[str] = Field(None, max_length=255)
    address: str
    state_code: str = Field(..., min_length=2, max_length=2, description="2-digit state code")
    turnover_slab: str = Field(..., description="below_1.5cr, 1.5cr_to_5cr, or above_5cr")
    filing_frequency: str = Field(default="monthly", description="monthly or quarterly")


class CompanyUpdate(BaseModel):
    """Schema for company update request."""
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    legal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    trade_name: Optional[str] = None
    address: Optional[str] = None
    state_code: Optional[str] = Field(None, min_length=2, max_length=2)
    turnover_slab: Optional[str] = None
    filing_frequency: Optional[str] = None


class CompanyResponse(BaseModel):
    """Schema for company response."""
    id: int
    user_id: int
    gstin: str
    legal_name: str
    trade_name: Optional[str]
    address: str
    state_code: str
    turnover_slab: str
    filing_frequency: str
    created_at: datetime
    
    class Config:
        from_attributes = True
