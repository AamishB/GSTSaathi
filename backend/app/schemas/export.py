"""
Export schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class GSTR1ExportRequest(BaseModel):
    """Schema for GSTR-1 export request."""
    format: str = Field(default="json", description="json or excel")
    month: Optional[str] = Field(None, description="MM-YYYY format")
    year: Optional[int] = Field(None, description="Financial year")


class GSTR3BExportRequest(BaseModel):
    """Schema for GSTR-3B export request."""
    format: str = Field(default="xlsx", description="xlsx only")
    month: Optional[str] = Field(None, description="MM-YYYY format")
    year: Optional[int] = Field(None, description="Financial year")


class MismatchReportExportRequest(BaseModel):
    """Schema for mismatch report export request."""
    format: str = Field(default="xlsx", description="xlsx or pdf")
    status: Optional[str] = Field(None, description="all, pending, resolved, reversed")


class ExportResponse(BaseModel):
    """Schema for export response."""
    success: bool
    message: str
    file_name: str
    file_size: int
    download_url: str
