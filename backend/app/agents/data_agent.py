"""
DataAgent for invoice data parsing and processing.
Uses smolagents CodeAgent with pandas-based tools.
"""
from typing import Dict, List, Any
from pathlib import Path
import pandas as pd

from .base_agent import BaseAgent
from ..services.upload_service import (
    parse_file,
    validate_invoice_dataframe,
    detect_duplicates,
    dataframe_to_invoices,
    dataframe_to_gstr2b_entries,
    generate_batch_id,
)


def create_data_agent() -> BaseAgent:
    """
    Create DataAgent with all data processing tools.
    
    Returns:
        Configured DataAgent
    """
    from smolagents import tool
    
    agent = BaseAgent(
        name="DataAgent",
        description="Parses Excel/CSV files, validates invoice data, detects duplicates, transforms to schema",
    )
    
    @tool
    def parse_excel_file(file_path: str) -> Dict:
        """
        Parse an Excel or CSV file and return structured data.
        
        Args:
            file_path: Path to the Excel/CSV file
            
        Returns:
            Dictionary with columns, row count, and sample data
        """
        try:
            df = parse_file(file_path)
            
            return {
                "success": True,
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_data": df.head(10).to_dict(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @tool
    def validate_invoice_data(file_path: str) -> Dict:
        """
        Validate invoice data from uploaded file.
        
        Args:
            file_path: Path to the Excel/CSV file
            
        Returns:
            Dictionary with valid records and errors
        """
        try:
            df = parse_file(file_path)
            valid_records, errors = validate_invoice_dataframe(df)
            
            return {
                "success": True,
                "valid_records_count": len(valid_records),
                "error_count": len(errors),
                "errors": errors,
                "valid_records": valid_records[:100],  # Limit sample
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @tool
    def check_duplicates_in_file(file_path: str) -> Dict:
        """
        Check for duplicate invoices within the uploaded file.
        
        Args:
            file_path: Path to the Excel/CSV file
            
        Returns:
            Dictionary with duplicate records
        """
        try:
            df = parse_file(file_path)
            
            # Check for duplicates
            if 'invoice_number' in df.columns and 'invoice_date' in df.columns and 'supplier_gstin' in df.columns:
                dup_mask = df.duplicated(subset=['invoice_number', 'invoice_date', 'supplier_gstin'], keep='first')
                dup_count = dup_mask.sum()
                
                duplicates = []
                for idx in df[dup_mask].index:
                    row = df.loc[idx]
                    duplicates.append({
                        "row": idx + 2,
                        "invoice_number": row.get('invoice_number'),
                        "invoice_date": str(row.get('invoice_date')),
                        "supplier_gstin": row.get('supplier_gstin'),
                    })
                
                return {
                    "success": True,
                    "duplicate_count": dup_count,
                    "duplicates": duplicates,
                }
            else:
                return {
                    "success": False,
                    "error": "Required columns not found (invoice_number, invoice_date, supplier_gstin)",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @tool
    def get_column_mapping(file_path: str) -> Dict:
        """
        Auto-detect column mapping from uploaded file.
        
        Args:
            file_path: Path to the Excel/CSV file
            
        Returns:
            Dictionary mapping detected columns to standard schema
        """
        try:
            df = parse_file(file_path)
            columns = [str(col).lower() for col in df.columns]
            
            # Standard column mappings
            mapping = {
                "invoice_number": None,
                "invoice_date": None,
                "supplier_gstin": None,
                "supplier_name": None,
                "recipient_gstin": None,
                "recipient_name": None,
                "taxable_value": None,
                "igst": None,
                "cgst": None,
                "sgst": None,
                "total_value": None,
                "hsn_code": None,
                "place_of_supply": None,
            }
            
            # Try to match columns
            for col in df.columns:
                col_lower = str(col).lower().replace(" ", "_").replace("-", "_")
                
                for standard_col in mapping.keys():
                    if standard_col in col_lower or col_lower in standard_col:
                        mapping[standard_col] = col
                        break
                    # Also check partial matches
                    if any(part in col_lower for part in standard_col.split("_")):
                        if mapping[standard_col] is None:
                            mapping[standard_col] = col
            
            return {
                "success": True,
                "detected_columns": columns,
                "mapping": mapping,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    # Register tools
    agent.add_tool(parse_excel_file)
    agent.add_tool(validate_invoice_data)
    agent.add_tool(check_duplicates_in_file)
    agent.add_tool(get_column_mapping)
    
    return agent


# Singleton instance
_data_agent = None


def get_data_agent() -> BaseAgent:
    """Get or create DataAgent singleton."""
    global _data_agent
    if _data_agent is None:
        _data_agent = create_data_agent()
    return _data_agent
