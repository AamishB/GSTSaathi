"""
Dashboard schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class DashboardMetrics(BaseModel):
    """Schema for dashboard metrics response."""
    total_sales: float = Field(..., description="Total outward supplies")
    total_purchases: float = Field(..., description="Total inward supplies")
    output_gst: float = Field(..., description="Total output GST liability")
    itc_available: float = Field(..., description="Eligible ITC available")
    net_gst_payable: float = Field(..., description="Net GST payable (output - ITC)")
    itc_at_risk: float = Field(..., description="Value of ITC at risk (missing invoices)")


class ITCAtRiskWidget(BaseModel):
    """Schema for ITC at risk widget response."""
    total_at_risk: float
    missing_invoices_count: int
    mismatched_invoices_count: int
    top_vendors: List[dict] = Field(default_factory=list)


class ComplianceScore(BaseModel):
    """Schema for compliance score response."""
    score: int = Field(..., ge=0, le=100, description="Compliance score 0-100")
    factors: dict = Field(default_factory=dict, description="Factors affecting score")
