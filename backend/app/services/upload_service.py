"""
Upload service for handling file uploads and parsing.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from ..config import settings
from ..models.invoice import Invoice
from ..models.gstr2b import GSTR2BEntry
from ..utils.gstin_validator import validate_gstin


def generate_batch_id() -> str:
    """Generate a unique batch ID for file uploads."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"BATCH_{timestamp}_{unique_id}"


def save_uploaded_file(file_content: bytes, filename: str, upload_type: str) -> Tuple[str, str]:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        upload_type: Type of upload ('invoices' or 'gstr2b')
        
    Returns:
        Tuple of (file_path, batch_id)
    """
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / upload_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_extension = Path(filename).suffix
    new_filename = f"{upload_type}_{timestamp}_{unique_id}{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    batch_id = generate_batch_id()
    
    return str(file_path), batch_id


def parse_excel_file(file_path: str) -> pd.DataFrame:
    """
    Parse an Excel file and return a DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        pandas DataFrame with file contents
    """
    return pd.read_excel(file_path)


def parse_csv_file(file_path: str) -> pd.DataFrame:
    """
    Parse a CSV file and return a DataFrame.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        pandas DataFrame with file contents
    """
    return pd.read_csv(file_path)


def parse_json_file(file_path: str) -> pd.DataFrame:
    """
    Parse a JSON file and return a DataFrame.

    Supports either:
    - a top-level list of records, or
    - a top-level object with one list-valued field.

    Args:
        file_path: Path to the JSON file

    Returns:
        pandas DataFrame with file contents
    """
    data = pd.read_json(file_path)

    # If read_json produced a Series-like single column object, normalize it.
    if isinstance(data, pd.Series):
        data = pd.DataFrame(data.tolist())

    # Handle object wrappers like {"data": [...]} by selecting the first list field.
    if isinstance(data, pd.DataFrame) and len(data.columns) == 1:
        col = data.columns[0]
        first_value = data.iloc[0][col] if len(data.index) > 0 else None
        if isinstance(first_value, list):
            data = pd.DataFrame(first_value)

    return data


def parse_file(file_path: str) -> pd.DataFrame:
    """
    Parse a file (Excel, CSV, or JSON) and return a DataFrame.
    
    Args:
        file_path: Path to the file
        
    Returns:
        pandas DataFrame with file contents
        
    Raises:
        ValueError: If file format is not supported
    """
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension in ['.xlsx', '.xls']:
        return parse_excel_file(file_path)
    elif file_extension in ['.csv']:
        return parse_csv_file(file_path)
    elif file_extension in ['.json']:
        return parse_json_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Use .xlsx, .csv or .json")


def validate_invoice_dataframe(df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate invoice DataFrame columns and data.
    
    Args:
        df: pandas DataFrame with invoice data
        
    Returns:
        Tuple of (valid_records, errors)
    """
    errors = []
    valid_records = []
    
    # Required columns
    required_columns = [
        'invoice_number', 'invoice_date', 'supplier_gstin', 'supplier_name',
        'recipient_gstin', 'recipient_name', 'taxable_value', 'total_value',
        'place_of_supply'
    ]
    
    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append({
            "type": "missing_columns",
            "message": f"Missing required columns: {missing_columns}",
        })
        return [], errors
    
    # Validate each row
    for idx, row in df.iterrows():
        row_errors = []
        
        # Validate GSTIN format
        supplier_gstin_result = validate_gstin(str(row.get('supplier_gstin', '')))
        if not supplier_gstin_result['valid']:
            row_errors.append(f"Invalid supplier GSTIN: {supplier_gstin_result['errors']}")
        
        recipient_gstin_result = validate_gstin(str(row.get('recipient_gstin', '')))
        if not recipient_gstin_result['valid']:
            row_errors.append(f"Invalid recipient GSTIN: {recipient_gstin_result['errors']}")
        
        # Validate taxable value
        try:
            taxable_value = float(row.get('taxable_value', 0))
            if taxable_value <= 0:
                row_errors.append("Taxable value must be positive")
        except (ValueError, TypeError):
            row_errors.append("Invalid taxable value")
        
        # Validate total value
        try:
            total_value = float(row.get('total_value', 0))
            if total_value <= 0:
                row_errors.append("Total value must be positive")
        except (ValueError, TypeError):
            row_errors.append("Invalid total value")
        
        if row_errors:
            errors.append({
                "row": idx + 2,  # Excel row number (1-indexed + header)
                "invoice_number": row.get('invoice_number', 'N/A'),
                "errors": row_errors,
            })
        else:
            valid_records.append(row.to_dict())
    
    return valid_records, errors


def detect_duplicates(
    df: pd.DataFrame,
    company_id: int,
    db: Session,
) -> List[Dict]:
    """
    Detect duplicate invoices within the same company.
    
    Duplicates are identified by: same invoice_number + invoice_date + supplier_gstin
    
    Args:
        df: pandas DataFrame with invoice data
        company_id: Company ID
        db: Database session
        
    Returns:
        List of duplicate records
    """
    duplicates = []
    
    # Check for duplicates within the uploaded file
    if 'invoice_number' in df.columns and 'invoice_date' in df.columns and 'supplier_gstin' in df.columns:
        dup_mask = df.duplicated(subset=['invoice_number', 'invoice_date', 'supplier_gstin'], keep='first')
        dup_rows = df[dup_mask]
        
        for idx, row in dup_rows.iterrows():
            duplicates.append({
                "row": idx + 2,
                "invoice_number": row.get('invoice_number'),
                "invoice_date": str(row.get('invoice_date')),
                "supplier_gstin": row.get('supplier_gstin'),
                "reason": "Duplicate within uploaded file",
            })
    
    # Check for duplicates in database
    existing_invoices = db.query(Invoice).filter(
        Invoice.company_id == company_id,
        Invoice.invoice_number.in_(df['invoice_number'].tolist()),
    ).all()
    
    if existing_invoices:
        existing_keys = {(inv.invoice_number, str(inv.invoice_date), inv.supplier_gstin) for inv in existing_invoices}
        
        for idx, row in df.iterrows():
            key = (row.get('invoice_number'), str(row.get('invoice_date')), row.get('supplier_gstin'))
            if key in existing_keys:
                duplicates.append({
                    "row": idx + 2,
                    "invoice_number": row.get('invoice_number'),
                    "invoice_date": str(row.get('invoice_date')),
                    "supplier_gstin": row.get('supplier_gstin'),
                    "reason": "Already exists in database",
                })
    
    return duplicates


def dataframe_to_invoices(
    df: pd.DataFrame,
    company_id: int,
    batch_id: str,
) -> List[Invoice]:
    """
    Convert a DataFrame to a list of Invoice objects.
    
    Args:
        df: pandas DataFrame with invoice data
        company_id: Company ID
        batch_id: Upload batch ID
        
    Returns:
        List of Invoice objects
    """
    invoices = []
    
    for _, row in df.iterrows():
        # Parse invoice date
        invoice_date = row.get('invoice_date')
        if isinstance(invoice_date, str):
            from datetime import datetime
            try:
                invoice_date = datetime.strptime(invoice_date, "%d-%m-%Y").date()
            except ValueError:
                try:
                    invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                except ValueError:
                    invoice_date = datetime.now().date()
        
        # Calculate tax amounts if not provided
        taxable_value = float(row.get('taxable_value', 0))
        total_value = float(row.get('total_value', 0))
        
        igst = float(row.get('igst', 0)) if row.get('igst') else 0
        cgst = float(row.get('cgst', 0)) if row.get('cgst') else 0
        sgst = float(row.get('sgst', 0)) if row.get('sgst') else 0
        place_of_supply = str(row.get('place_of_supply', '')).zfill(2)
        
        # If tax amounts not provided, calculate from total
        if igst == 0 and cgst == 0 and sgst == 0:
            tax_amount = total_value - taxable_value
            # For simplicity, assume intra-state if place matches company state
            # This is a simplification - real logic would need company state
            igst = tax_amount  # Default to IGST
        
        invoice = Invoice(
            company_id=company_id,
            invoice_number=str(row.get('invoice_number')),
            invoice_date=invoice_date,
            supplier_gstin=str(row.get('supplier_gstin', '')).upper(),
            supplier_name=str(row.get('supplier_name', '')),
            recipient_gstin=str(row.get('recipient_gstin', '')).upper(),
            recipient_name=str(row.get('recipient_name', '')),
            taxable_value=taxable_value,
            igst=igst,
            cgst=cgst,
            sgst=sgst,
            total_value=total_value,
            hsn_code=str(row.get('hsn_code')) if row.get('hsn_code') else None,
            place_of_supply=place_of_supply,
            upload_batch_id=batch_id,
        )
        invoices.append(invoice)
    
    return invoices


def dataframe_to_gstr2b_entries(
    df: pd.DataFrame,
    company_id: int,
    batch_id: str,
) -> List[GSTR2BEntry]:
    """
    Convert a DataFrame to a list of GSTR2BEntry objects.
    
    Args:
        df: pandas DataFrame with GSTR-2B data
        company_id: Company ID
        batch_id: Import batch ID
        
    Returns:
        List of GSTR2BEntry objects
    """
    entries = []
    
    for _, row in df.iterrows():
        # Parse invoice date
        invoice_date = row.get('invoice_date')
        if isinstance(invoice_date, str):
            from datetime import datetime
            try:
                invoice_date = datetime.strptime(invoice_date, "%d-%m-%Y").date()
            except ValueError:
                try:
                    invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                except ValueError:
                    invoice_date = datetime.now().date()
        
        # Determine ITC eligibility
        itc_eligible = row.get('itc_eligible', True)
        if isinstance(itc_eligible, str):
            itc_eligible = itc_eligible.lower() in ['yes', 'true', '1', 'eligible']
        
        itc_ineligible_reason = row.get('itc_ineligible_reason')
        
        entry = GSTR2BEntry(
            company_id=company_id,
            supplier_gstin=str(row.get('supplier_gstin', '')).upper(),
            invoice_number=str(row.get('invoice_number')),
            invoice_date=invoice_date,
            taxable_value=float(row.get('taxable_value', 0)),
            igst=float(row.get('igst', 0)) if row.get('igst') else 0,
            cgst=float(row.get('cgst', 0)) if row.get('cgst') else 0,
            sgst=float(row.get('sgst', 0)) if row.get('sgst') else 0,
            itc_eligible=itc_eligible,
            itc_ineligible_reason=str(itc_ineligible_reason) if itc_ineligible_reason else None,
            import_batch_id=batch_id,
        )
        entries.append(entry)
    
    return entries
