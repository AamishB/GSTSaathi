"""
Pydantic schemas for GSTSaathi API.
"""
from .auth import UserCreate, UserLogin, Token, TokenData, UserResponse
from .company import CompanyCreate, CompanyUpdate, CompanyResponse
from .invoice import InvoiceCreate, InvoiceResponse, InvoiceUploadResponse
from .reconciliation import (
    ReconciliationResultSchema,
    ReconciliationRunRequest,
    ReconciliationRunResponse,
    ReconciliationStatusResponse,
    ReconciliationResultsResponse,
    MismatchRecord,
)
from .export import GSTR1ExportRequest, GSTR3BExportRequest, MismatchReportExportRequest, ExportResponse
from .dashboard import DashboardMetrics, ITCAtRiskWidget, ComplianceScore

__all__ = [
    # Auth
    "UserCreate",
    "UserLogin",
    "Token",
    "TokenData",
    "UserResponse",
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    # Invoice
    "InvoiceCreate",
    "InvoiceResponse",
    "InvoiceUploadResponse",
    # Reconciliation
    "ReconciliationResultSchema",
    "ReconciliationRunRequest",
    "ReconciliationRunResponse",
    "ReconciliationStatusResponse",
    "ReconciliationResultsResponse",
    "MismatchRecord",
    # Export
    "GSTR1ExportRequest",
    "GSTR3BExportRequest",
    "MismatchReportExportRequest",
    "ExportResponse",
    # Dashboard
    "DashboardMetrics",
    "ITCAtRiskWidget",
    "ComplianceScore",
]
