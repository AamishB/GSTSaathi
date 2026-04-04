"""
Export API routes for GSTR-1, GSTR-3B, and report generation.
Integrated with FilingAgent for document generation.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO

from ..database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.company import Company
from ..models.invoice import Invoice
from ..models.reconciliation import ReconciliationResult
from ..agents.filing_agent import get_filing_agent
from ..utils.agent_logging import log_agent_event

router = APIRouter(prefix="/export", tags=["Export"])
logger = logging.getLogger("gstsaathi.agents")


@router.get("/gstr1")
async def export_gstr1(
    format: str = "json",
    month: str = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export GSTR-1 data in JSON format for offline tool.
    Uses FilingAgent for document generation.
    
    Args:
        format: Export format (json)
        month: Month (MM)
        year: Year (YYYY)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        GSTR-1 JSON file download
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Default to current month/year
    if not month:
        month = datetime.now().strftime("%m")
    if not year:
        year = datetime.now().year
    
    period = f"{month}-{year}"
    
    # Get invoices for the period
    invoices = db.query(Invoice).filter(
        Invoice.company_id == company.id
    ).all()
    
    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No invoices found for period {period}",
        )
    
    # Convert to dictionaries
    invoices_dict = [
        {
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date.strftime("%Y-%m-%d") if isinstance(inv.invoice_date, datetime) else str(inv.invoice_date),
            "recipient_gstin": inv.recipient_gstin,
            "recipient_name": inv.recipient_name,
            "taxable_value": inv.taxable_value,
            "igst": inv.igst,
            "cgst": inv.cgst,
            "sgst": inv.sgst,
            "total_value": inv.total_value,
            "place_of_supply": inv.place_of_supply,
            "hsn_code": inv.hsn_code,
        }
        for inv in invoices
    ]
    
    # Use FilingAgent to generate GSTR-1
    filing_agent = get_filing_agent()
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate GSTR-1 return",
        status="started",
        user_id=current_user.id,
        details={"invoice_count": len(invoices_dict), "period": period},
    )
    result = filing_agent.execute(
        "Generate GSTR-1 return",
        {
            "invoices": invoices_dict,
            "company_gstin": company.gstin,
            "period": period,
        }
    )
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate GSTR-1 return",
        status="success" if result.get("success") else "failed",
        user_id=current_user.id,
        details={"period": period},
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate GSTR-1",
        )
    
    # Return as JSON download
    filename = f"GSTR1_{company.gstin}_{period}.json"
    
    return JSONResponse(
        content=result.get("gstr1_data", {}),
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json",
        },
    )


@router.get("/gstr3b")
async def export_gstr3b(
    format: str = "xlsx",
    month: str = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export GSTR-3B summary in Excel format.
    Uses FilingAgent for document generation.
    
    Args:
        format: Export format (xlsx)
        month: Month (MM)
        year: Year (YYYY)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        GSTR-3B Excel file download
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Default to current month/year
    if not month:
        month = datetime.now().strftime("%m")
    if not year:
        year = datetime.now().year
    
    period = f"{month}-{year}"
    
    # Get invoices
    invoices = db.query(Invoice).filter(Invoice.company_id == company.id).all()
    
    # Calculate output GST
    output_igst = sum(inv.igst for inv in invoices)
    output_cgst = sum(inv.cgst for inv in invoices)
    output_sgst = sum(inv.sgst for inv in invoices)
    
    output_gst = {
        "igst": output_igst,
        "cgst": output_cgst,
        "sgst": output_sgst,
    }
    
    # Calculate eligible ITC (from matched invoices)
    matched_results = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'matched'
    ).all()
    
    eligible_itc = {
        "igst": sum(r.invoice.igst for r in matched_results),
        "cgst": sum(r.invoice.cgst for r in matched_results),
        "sgst": sum(r.invoice.sgst for r in matched_results),
    }
    
    # Use FilingAgent to generate GSTR-3B
    filing_agent = get_filing_agent()
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate GSTR-3B return",
        status="started",
        user_id=current_user.id,
        details={"invoice_count": len(invoices), "period": period},
    )
    result = filing_agent.execute(
        "Generate GSTR-3B return",
        {
            "output_gst": output_gst,
            "eligible_itc": eligible_itc,
            "period": period,
        }
    )
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate GSTR-3B return",
        status="success" if result.get("success") else "failed",
        user_id=current_user.id,
        details={"period": period},
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate GSTR-3B",
        )
    
    # Return as file download
    filename = f"GSTR3B_{company.gstin}_{period}.xlsx"
    excel_data = result.get("excel_data")
    
    if excel_data:
        return StreamingResponse(
            BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Excel file",
        )


@router.get("/mismatch-report")
async def export_mismatch_report(
    format: str = "xlsx",
    status_filter: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export mismatch report in Excel format.
    
    Args:
        format: Export format (xlsx)
        status_filter: Filter by status (all, pending, resolved)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Mismatch report Excel file download
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Get mismatched reconciliation results
    query = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status != 'matched'
    )
    
    if status_filter == 'pending':
        query = query.filter(ReconciliationResult.action_taken == 'pending')
    elif status_filter == 'resolved':
        query = query.filter(ReconciliationResult.action_taken == 'resolved')
    
    results = query.all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No mismatches found",
        )
    
    # Format mismatches for report
    mismatches = []
    for r in results:
        mismatches.append({
            "invoice_number": r.invoice.invoice_number,
            "invoice_date": str(r.invoice.invoice_date),
            "supplier_gstin": r.invoice.supplier_gstin,
            "supplier_name": r.invoice.supplier_name,
            "booked_taxable_value": r.invoice.taxable_value,
            "gstr2b_taxable_value": r.invoice.taxable_value - r.taxable_value_diff if r.taxable_value_diff else None,
            "tax_difference": r.tax_value_diff or 0,
            "mismatch_type": r.mismatch_category or r.match_status,
            "action_taken": r.action_taken,
        })
    
    # Use FilingAgent to generate report
    filing_agent = get_filing_agent()
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate mismatch report",
        status="started",
        user_id=current_user.id,
        details={"mismatch_count": len(mismatches), "status_filter": status_filter},
    )
    result = filing_agent.execute(
        "Generate mismatch report",
        {
            "mismatches": mismatches,
            "company_name": company.legal_name,
            "period": datetime.now().strftime("%m-%Y"),
        }
    )
    log_agent_event(
        logger,
        agent="FilingAgent",
        task="Generate mismatch report",
        status="success" if result.get("success") else "failed",
        user_id=current_user.id,
        details={"mismatch_count": len(mismatches)},
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate mismatch report",
        )
    
    # Return as file download
    filename = f"Mismatch_Report_{company.gstin}_{datetime.now().strftime('%m-%Y')}.xlsx"
    excel_data = result.get("excel_data")
    
    if excel_data:
        return StreamingResponse(
            BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Excel file",
        )
