"""
Reconciliation API routes.
Integrated with ReconciliationAgent and ComplianceAgent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from datetime import datetime
import uuid
import json

from ..database import get_db
from ..schemas.reconciliation import (
    ReconciliationRunResponse,
    ReconciliationStatusResponse,
    ReconciliationResultsResponse,
    ReconciliationResultSchema,
    ReconciliationLogResponse,
    ReconciliationLogItem,
)
from ..api.deps import get_current_user
from ..models.user import User
from ..models.company import Company
from ..models.invoice import Invoice
from ..models.gstr2b import GSTR2BEntry
from ..models.reconciliation import ReconciliationResult
from ..models.reconciliation_log import ReconciliationLog
from ..agents.reconciliation_agent import get_reconciliation_agent
from ..agents.compliance_agent import get_compliance_agent

router = APIRouter(prefix="/reconcile", tags=["Reconciliation"])


@router.post("/run", response_model=ReconciliationRunResponse)
async def run_reconciliation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run invoice reconciliation with GSTR-2B.
    Uses ReconciliationAgent for matching and ComplianceAgent for ITC calculation.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Reconciliation job status
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Check if we have invoices and GSTR-2B data
    invoice_count = db.query(Invoice).filter(Invoice.company_id == company.id).count()
    gstr2b_count = db.query(GSTR2BEntry).filter(GSTR2BEntry.company_id == company.id).count()
    
    if invoice_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No invoices uploaded. Please upload invoices first.",
        )
    
    if gstr2b_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GSTR-2B data uploaded. Please upload GSTR-2B first.",
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Perform reconciliation using agents
    try:
        # Load invoices into DataFrame
        invoices = db.query(Invoice).filter(Invoice.company_id == company.id).all()
        invoices_df = pd.DataFrame([
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "invoice_date": inv.invoice_date,
                "supplier_gstin": inv.supplier_gstin,
                "supplier_name": inv.supplier_name,
                "taxable_value": inv.taxable_value,
                "igst": inv.igst,
                "cgst": inv.cgst,
                "sgst": inv.sgst,
            }
            for inv in invoices
        ])
        
        # Load GSTR-2B entries into DataFrame
        gstr2b_entries = db.query(GSTR2BEntry).filter(GSTR2BEntry.company_id == company.id).all()
        gstr2b_df = pd.DataFrame([
            {
                "id": entry.id,
                "invoice_number": entry.invoice_number,
                "invoice_date": entry.invoice_date,
                "supplier_gstin": entry.supplier_gstin,
                "taxable_value": entry.taxable_value,
                "igst": entry.igst,
                "cgst": entry.cgst,
                "sgst": entry.sgst,
                "itc_eligible": entry.itc_eligible,
            }
            for entry in gstr2b_entries
        ])
        
        # Use ReconciliationAgent to match invoices
        reconciliation_agent = get_reconciliation_agent()
        match_result = reconciliation_agent.execute(
            "Match invoices with GSTR-2B data",
            {"invoices_df": invoices_df, "gstr2b_df": gstr2b_df}
        )
        
        if not match_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Reconciliation failed",
            )
        
        # Save reconciliation results to database
        results = _save_reconciliation_results(
            db, company.id, match_result.get("matches", []), invoices, gstr2b_entries
        )

        # Persist reconciliation run log (F42).
        log = ReconciliationLog(
            company_id=company.id,
            job_id=job_id,
            matched_count=results["matched"],
            mismatch_count=results["mismatched"],
            itc_at_risk=float(match_result.get("itc_at_risk", 0) or 0),
            status="completed",
        )
        db.add(log)
        db.commit()
        
        return ReconciliationRunResponse(
            status="completed",
            job_id=job_id,
            message=f"Reconciliation completed: {results['matched']} matched, {results['mismatched']} mismatched",
        )
        
    except Exception as e:
        # Best-effort failed run log.
        try:
            failed_log = ReconciliationLog(
                company_id=company.id,
                job_id=job_id,
                matched_count=0,
                mismatch_count=0,
                itc_at_risk=0,
                status="failed",
            )
            db.add(failed_log)
            db.commit()
        except Exception:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation failed: {str(e)}",
        )


def _save_reconciliation_results(
    db: Session,
    company_id: int,
    matches: list,
    invoices: list,
    gstr2b_entries: list,
) -> dict:
    """
    Save reconciliation results to database.
    """
    # Clear existing results for this company
    existing_results = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company_id
    ).all()
    for r in existing_results:
        db.delete(r)
    db.commit()
    
    results = {'matched': 0, 'mismatched': 0}
    
    for match in matches:
        # Find invoice by invoice_number
        invoice = next((inv for inv in invoices if inv.invoice_number == match.get('invoice_number')), None)
        if not invoice:
            continue
        
        # Find GSTR-2B entry if matched
        gstr2b_entry = None
        if match.get('_merge') == 'both' or match.get('match_status') == 'matched':
            gstr2b_entry = next((e for e in gstr2b_entries if e.invoice_number == match.get('invoice_number')), None)
        
        # Calculate differences
        taxable_value_diff = None
        tax_value_diff = None
        
        if match.get('match_status') == 'value_mismatch':
            taxable_value_diff = abs(match.get('taxable_value_inv', 0) - match.get('taxable_value_gstr2b', 0))
            tax_value_diff = abs(
                (match.get('igst_inv', 0) + match.get('cgst_inv', 0) + match.get('sgst_inv', 0)) -
                (match.get('igst_gstr2b', 0) + match.get('cgst_gstr2b', 0) + match.get('sgst_gstr2b', 0))
            )
        
        # Create reconciliation result
        result = ReconciliationResult(
            invoice_id=invoice.id,
            gstr2b_entry_id=gstr2b_entry.id if gstr2b_entry else None,
            match_status=match.get('match_status', 'missing_in_gstr2b'),
            match_confidence='exact' if match.get('match_status') == 'matched' else 'partial',
            taxable_value_diff=taxable_value_diff,
            tax_value_diff=tax_value_diff,
            mismatch_category=match.get('match_status') if match.get('match_status') != 'matched' else None,
            action_taken='pending' if match.get('match_status') != 'matched' else 'resolved',
        )
        
        db.add(result)
        
        if match.get('match_status') == 'matched':
            results['matched'] += 1
        else:
            results['mismatched'] += 1
    
    db.commit()
    return results


@router.get("/status/{job_id}")
async def get_reconciliation_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get reconciliation status for a job.
    
    Args:
        job_id: Reconciliation job ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Reconciliation status and statistics
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Get reconciliation statistics
    total = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id
    ).count()
    
    matched = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'matched'
    ).count()
    
    mismatched = total - matched
    
    # Calculate ITC eligible (from matched invoices)
    itc_eligible = db.query(
        Invoice.igst + Invoice.cgst + Invoice.sgst
    ).join(ReconciliationResult).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'matched'
    ).scalar() or 0
    
    # Calculate ITC at risk (from missing invoices)
    itc_at_risk = db.query(
        Invoice.igst + Invoice.cgst + Invoice.sgst
    ).join(ReconciliationResult).filter(
        Invoice.company_id == company.id,
        ReconciliationResult.match_status == 'missing_in_gstr2b'
    ).scalar() or 0
    
    return ReconciliationStatusResponse(
        status="completed",
        job_id=job_id,
        matched_count=matched,
        mismatch_count=mismatched,
        itc_eligible=round(itc_eligible, 2),
        itc_at_risk=round(itc_at_risk, 2),
    )


@router.get("/results", response_model=ReconciliationResultsResponse)
async def get_reconciliation_results(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get reconciliation results.
    
    Args:
        status_filter: Filter by status (all, matched, mismatched)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of reconciliation results
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    # Query results
    query = db.query(ReconciliationResult).join(Invoice).filter(
        Invoice.company_id == company.id
    )
    
    if status_filter == 'matched':
        query = query.filter(ReconciliationResult.match_status == 'matched')
    elif status_filter == 'mismatched':
        query = query.filter(ReconciliationResult.match_status != 'matched')
    
    results = query.all()
    
    # Convert to schema
    result_schemas = []
    for r in results:
        result_schemas.append(ReconciliationResultSchema(
            id=r.id,
            invoice_id=r.invoice_id,
            invoice_number=r.invoice.invoice_number,
            supplier_gstin=r.invoice.supplier_gstin,
            invoice_date=r.invoice.invoice_date,
            taxable_value=r.invoice.taxable_value,
            match_status=r.match_status,
            match_confidence=r.match_confidence,
            taxable_value_diff=r.taxable_value_diff,
            tax_value_diff=r.tax_value_diff,
            mismatch_category=r.mismatch_category,
            action_taken=r.action_taken,
            reconciled_at=r.reconciled_at,
        ))
    
    matched_count = sum(1 for r in result_schemas if r.match_status == 'matched')
    mismatch_count = len(result_schemas) - matched_count
    
    return ReconciliationResultsResponse(
        results=result_schemas,
        total=len(result_schemas),
        matched_count=matched_count,
        mismatch_count=mismatch_count,
    )


@router.get("/log", response_model=ReconciliationLogResponse)
async def get_reconciliation_log(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get reconciliation run history for current user's company (F42)."""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    rows = db.query(ReconciliationLog).filter(
        ReconciliationLog.company_id == company.id
    ).order_by(ReconciliationLog.created_at.desc()).all()

    return ReconciliationLogResponse(
        logs=[
            ReconciliationLogItem(
                id=row.id,
                job_id=row.job_id,
                matched_count=row.matched_count,
                mismatch_count=row.mismatch_count,
                itc_at_risk=row.itc_at_risk,
                status=row.status,
                created_at=row.created_at,
            )
            for row in rows
        ],
        total=len(rows),
    )
