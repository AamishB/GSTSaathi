"""
Data Agent - Uses smolagents to parse Excel/CSV invoice data
Updated for smolagents 1.24.0
"""
import pandas as pd
import json
from typing import Dict, Any
from smolagents import Tool


class ExcelDataExtractor(Tool):
    """Extract invoice data from Excel file"""
    name = "excel_extractor"
    description = "Extracts invoice data from Excel file with columns: invoice_number, invoice_date, vendor_name, vendor_gstin, taxable_value, cgst, sgst, igst, total_value"
    inputs = {
        "file_path": {"type": "string", "description": "Path to the Excel file"}
    }
    output_type = "any"
    
    def forward(self, file_path: str) -> Any:
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Convert to list of dicts
            invoices = df.to_dict('records')
            
            # Ensure all required fields exist
            required_fields = ['invoice_number', 'invoice_date', 'vendor_name', 
                             'vendor_gstin', 'taxable_value', 'cgst', 'sgst', 'igst', 'total_value']
            
            for invoice in invoices:
                for field in required_fields:
                    if field not in invoice:
                        invoice[field] = 0 if 'value' in field.lower() else ""
            
            return invoices
        except Exception as e:
            return {"error": str(e)}


class CSVDataExtractor(Tool):
    """Extract invoice data from CSV file"""
    name = "csv_extractor"
    description = "Extracts invoice data from CSV file"
    inputs = {
        "file_path": {"type": "string", "description": "Path to the CSV file"}
    }
    output_type = "any"
    
    def forward(self, file_path: str) -> Any:
        try:
            df = pd.read_csv(file_path)
            invoices = df.to_dict('records')
            return invoices
        except Exception as e:
            return {"error": str(e)}


def parse_invoice_data(file_path: str, file_type: str = "excel") -> dict:
    """
    Parse invoice data from file using pandas (simplified approach without LLM)
    Returns structured data
    """
    try:
        if file_type == "excel":
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            df = pd.read_csv(file_path)
        
        # Calculate totals
        total_sales = df['total_value'].sum() if 'total_value' in df.columns else 0
        total_taxable = df['taxable_value'].sum() if 'taxable_value' in df.columns else 0
        total_cgst = df['cgst'].sum() if 'cgst' in df.columns else 0
        total_sgst = df['sgst'].sum() if 'sgst' in df.columns else 0
        total_igst = df['igst'].sum() if 'igst' in df.columns else 0
        
        # Convert to list of dicts
        invoices = df.to_dict('records')
        
        return {
            "success": True,
            "invoices": invoices,
            "count": len(invoices),
            "totals": {
                "total_sales": float(total_sales),
                "total_taxable": float(total_taxable),
                "total_cgst": float(total_cgst),
                "total_sgst": float(total_sgst),
                "total_igst": float(total_igst),
                "gst_payable": float(total_cgst + total_sgst + total_igst)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "invoices": [],
            "count": 0,
            "totals": {}
        }
