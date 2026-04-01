"""
Dashboard API routes for metrics and compliance overview.
Integrated with ComplianceAgent for calculations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from ..database import get_db
from ..schemas.dashboard import DashboardMetrics
from ..api.deps import get_current_user
from ..models.user import User
from ..models.company import Company
from ..models.invoice import Invoice
from ..models.gstr2b import GSTR2BEntry
from ..models.reconciliation import ReconciliationResult

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get dashboard metrics for current user's company.
    Uses ComplianceAgent for ITC and GST calculations.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dashboard metrics including sales, purchases, GST, ITC
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please create company profile first.",
        )
    
    # Load all data for deterministic metric calculation.
    invoices = db.query(Invoice).filter(Invoice.company_id == company.id).all()
    gstr2b_entries = db.query(GSTR2BEntry).filter(GSTR2BEntry.company_id == company.id).all()
    reconciliation_results = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id
    ).all()

    total_sales = sum(float(inv.total_value or 0) for inv in invoices)
    output_gst = sum(
        float(inv.igst or 0) + float(inv.cgst or 0) + float(inv.sgst or 0)
        for inv in invoices
    )

    total_purchases = sum(float(entry.taxable_value or 0) for entry in gstr2b_entries)
    itc_available = sum(
        float(entry.igst or 0) + float(entry.cgst or 0) + float(entry.sgst or 0)
        for entry in gstr2b_entries
        if entry.itc_eligible
    )

    reconciliation_map = {r.invoice_id: r.match_status for r in reconciliation_results}
    itc_at_risk = sum(
        float(inv.igst or 0) + float(inv.cgst or 0) + float(inv.sgst or 0)
        for inv in invoices
        if reconciliation_map.get(inv.id, "missing_in_gstr2b") == "missing_in_gstr2b"
    )

    net_gst_payable = output_gst - itc_available
    
    return DashboardMetrics(
        total_sales=round(total_sales, 2),
        total_purchases=round(total_purchases, 2),
        output_gst=round(output_gst, 2),
        itc_available=round(itc_available, 2),
        net_gst_payable=round(net_gst_payable, 2),
        itc_at_risk=round(itc_at_risk, 2),
    )


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get dashboard summary with additional statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dashboard summary with counts and statistics
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Invoice counts
    total_invoices = db.query(Invoice).filter(Invoice.company_id == company.id).count()
    
    # Reconciliation counts
    matched_count = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'matched'
    ).count()
    
    missing_count = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'missing_in_gstr2b'
    ).count()
    
    value_mismatch_count = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'value_mismatch'
    ).count()
    
    # GSTR-2B entries
    gstr2b_count = db.query(GSTR2BEntry).filter(GSTR2BEntry.company_id == company.id).count()
    
    # Calculate compliance score (simple formula for MVP)
    if total_invoices > 0:
        compliance_score = int((matched_count / total_invoices) * 100)
    else:
        compliance_score = 0
    
    return {
        "total_invoices": total_invoices,
        "gstr2b_entries": gstr2b_count,
        "reconciliation": {
            "matched": matched_count,
            "missing": missing_count,
            "value_mismatch": value_mismatch_count,
        },
        "compliance_score": compliance_score,
        "match_percentage": round((matched_count / total_invoices * 100) if total_invoices > 0 else 0, 2),
    }
