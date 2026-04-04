"""
Upload API routes for invoice and GSTR-2B file uploads.
Integrated with DataAgent and ValidatorAgent.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timezone
import pandas as pd
from pathlib import Path

from ..database import get_db
from ..schemas.invoice import InvoiceUploadResponse
from ..api.deps import get_current_user
from ..models.user import User
from ..services.upload_service import (
    save_uploaded_file,
    parse_file,
    validate_invoice_dataframe,
    detect_duplicates,
    normalize_invoice_key,
    dataframe_to_invoices,
    dataframe_to_gstr2b_entries,
    generate_batch_id,
)
from ..models.invoice import Invoice
from ..models.gstr2b import GSTR2BEntry
from ..models.company import Company
from ..agents.data_agent import get_data_agent
from ..agents.validator_agent import get_validator_agent
from ..utils.agent_logging import log_agent_event
router = APIRouter(prefix="/upload", tags=["Upload"])

logger = logging.getLogger("gstsaathi.agents")


def serialize_utc_datetime(dt):
    """Return ISO string with timezone for consistent frontend rendering."""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat()


@router.post("/invoices", response_model=InvoiceUploadResponse)
async def upload_invoices(
    file: UploadFile = File(...),
    turnover_slab: str = Form(default="1.5cr_to_5cr"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload invoice Excel/CSV file.
    Uses DataAgent for parsing and ValidatorAgent for GSTIN validation.
    
    Args:
        file: Excel or CSV file with invoice data
        turnover_slab: Company turnover slab
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Upload result with invoice count and errors
    """
    # Get company for user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please create company profile first.",
        )
    
    # Validate file type
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_ext = file.filename[-5:].lower()
    if not any(file_ext.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
        )
    
    try:
        data_agent = get_data_agent()
        validator_agent = get_validator_agent()

        # Read file content
        file_content = await file.read()
        
        # Save file
        file_path, batch_id = save_uploaded_file(file_content, file.filename, "invoices")
        
        # Parse uploaded file and run deterministic validation/duplicate checks.
        parse_result = data_agent.execute(
            "Parse invoice file",
            {"file_path": file_path, "action": "parse"},
        )
        log_agent_event(
            logger,
            agent="DataAgent",
            task="Parse invoice file",
            status="success" if parse_result.get("success") else "failed",
            user_id=current_user.id,
            details={
                "file": file.filename,
                "row_count": parse_result.get("row_count"),
                "error": parse_result.get("error"),
            },
        )
        if not parse_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to parse invoice file: {parse_result.get('error', 'Unknown error')}",
            )

        df = parse_file(file_path)

        gstin_validation = validator_agent.execute(
            "Validate GSTINs in dataframe",
            {"dataframe": df, "column": "supplier_gstin"},
        )
        log_agent_event(
            logger,
            agent="ValidatorAgent",
            task="Validate GSTINs in dataframe",
            status="success" if gstin_validation.get("success") else "failed",
            user_id=current_user.id,
            details={
                "invalid_count": gstin_validation.get("invalid_count"),
                "total": gstin_validation.get("total"),
            },
        )
        _, validation_errors = validate_invoice_dataframe(df)
        duplicates = detect_duplicates(df, company.id, db)
        duplicate_check = data_agent.execute(
            "Check duplicates",
            {"file_path": file_path, "action": "duplicates"},
        )
        log_agent_event(
            logger,
            agent="DataAgent",
            task="Check duplicates",
            status="success" if duplicate_check.get("success") else "failed",
            user_id=current_user.id,
            details={
                "duplicate_count": duplicate_check.get("duplicate_count"),
                "error": duplicate_check.get("error"),
            },
        )
        
        # Convert to invoices
        invoices = dataframe_to_invoices(df, company.id, batch_id)
        
        # Mark duplicates
        duplicate_keys = {
            normalize_invoice_key(
                d.get("invoice_number"),
                d.get("invoice_date"),
                d.get("supplier_gstin"),
            )
            for d in duplicates
        }
        for inv in invoices:
            key = normalize_invoice_key(inv.invoice_number, inv.invoice_date, inv.supplier_gstin)
            if key in duplicate_keys:
                inv.is_duplicate = True

        invoices_to_insert = [inv for inv in invoices if not inv.is_duplicate]
        
        # Save to database
        db.add_all(invoices_to_insert)
        db.commit()
        
        # Calculate totals
        total_value = sum(inv.total_value for inv in invoices_to_insert)
        duplicate_count = sum(1 for inv in invoices if inv.is_duplicate)
        
        # Collect errors
        errors = []
        if validation_errors:
            errors.extend(validation_errors[:50])
        if gstin_validation.get("success") and gstin_validation.get("errors"):
            for e in gstin_validation.get("errors", [])[:50]:
                errors.append({"row": e.get("row"), "error": f"Invalid supplier GSTIN: {e.get('gstin')}"})
        if duplicates:
            errors.extend([{"row": d.get("row"), "error": f"Duplicate invoice: {d.get('invoice_number')}"} for d in duplicates[:50]])
        if duplicate_check.get("success") and duplicate_check.get("duplicate_count", 0) > 0 and not duplicates:
            errors.append({"error": f"Detected {duplicate_check.get('duplicate_count')} in-file duplicates"})
        
        return InvoiceUploadResponse(
            success=True,
            message=f"Uploaded {len(invoices_to_insert)} invoices ({duplicate_count} duplicates skipped)",
            invoice_count=len(invoices_to_insert),
            total_value=total_value,
            duplicate_count=duplicate_count,
            errors=errors,
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.post("/gstr2b")
async def upload_gstr2b(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload GSTR-2B JSON/Excel file.
    Uses DataAgent for parsing.
    
    Args:
        file: GSTR-2B JSON or Excel file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Upload result with entry count
    """
    # Get company for user
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file
        file_path, batch_id = save_uploaded_file(file_content, file.filename, "gstr2b")
        
        # Parse file for database insertion
        df = parse_file(file_path)
        
        # Convert to GSTR-2B entries
        entries = dataframe_to_gstr2b_entries(df, company.id, batch_id)
        
        # Save to database
        db.add_all(entries)
        db.commit()
        
        # Calculate totals
        total_itc = sum(e.igst + e.cgst + e.sgst for e in entries if e.itc_eligible)
        
        return {
            "success": True,
            "message": f"Uploaded {len(entries)} GSTR-2B entries",
            "entry_count": len(entries),
            "total_itc": round(total_itc, 2),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/history")
async def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get upload history for current user's company.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of upload records
    """
    # Get company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        return []
    
    # Get invoice upload batches
    invoice_batches = db.query(
        Invoice.upload_batch_id,
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total_value).label('total_value'),
        func.max(Invoice.created_at).label('created_at'),
    ).filter(
        Invoice.company_id == company.id,
        Invoice.upload_batch_id.isnot(None)
    ).group_by(Invoice.upload_batch_id).all()
    
    # Get GSTR-2B import batches
    gstr2b_batches = db.query(
        GSTR2BEntry.import_batch_id,
        func.count(GSTR2BEntry.id).label('count'),
        func.sum(GSTR2BEntry.taxable_value).label('total_value'),
        func.max(GSTR2BEntry.created_at).label('created_at'),
    ).filter(
        GSTR2BEntry.company_id == company.id,
    ).group_by(GSTR2BEntry.import_batch_id).all()
    
    # Combine results
    history = []
    
    for batch in invoice_batches:
        history.append({
            "batch_id": batch.upload_batch_id,
            "type": "invoices",
            "count": batch.count,
            "total_value": float(batch.total_value) if batch.total_value else 0,
            "created_at": serialize_utc_datetime(batch.created_at),
        })
    
    for batch in gstr2b_batches:
        history.append({
            "batch_id": batch.import_batch_id,
            "type": "gstr2b",
            "count": batch.count,
            "total_value": float(batch.total_value) if batch.total_value else 0,
            "created_at": serialize_utc_datetime(batch.created_at),
        })
    
    # Sort by date
    history.sort(key=lambda x: x['created_at'] or '', reverse=True)
    
    return history
