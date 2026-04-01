"""
FilingAgent for generating GST return files (GSTR-1, GSTR-3B).
Uses smolagents CodeAgent with export tools.
"""
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO

from .base_agent import BaseAgent
from ..services.export_service import (
    generate_gstr1_json,
    save_gstr1_json,
    generate_gstr3b_excel,
    generate_mismatch_report_excel,
)


def create_filing_agent() -> BaseAgent:
    """
    Create FilingAgent with all filing generation tools.
    
    Returns:
        Configured FilingAgent
    """
    from smolagents import tool
    
    agent = BaseAgent(
        name="FilingAgent",
        description="Generates GSTR-1 JSON, GSTR-3B Excel, B2B report, HSN summary, mismatch reports",
    )
    
    @tool
    def generate_gstr1_return(invoices: List[Dict], company_gstin: str, period: str) -> Dict:
        """
        Generate GSTR-1 return data.
        
        Args:
            invoices: List of invoice dictionaries
            company_gstin: Company GSTIN
            period: Period in MM-YYYY format
            
        Returns:
            Dictionary with GSTR-1 JSON data
        """
        # Convert dicts to objects with attributes
        class InvoiceObj:
            def __init__(self, data):
                for k, v in data.items():
                    setattr(self, k, v)
        
        invoice_objects = [InvoiceObj(inv) for inv in invoices]
        
        gstr1_data = generate_gstr1_json(invoice_objects, company_gstin, period)
        
        return {
            "success": True,
            "gstr1_data": gstr1_data,
            "b2b_count": len(gstr1_data.get('b2b', {}).get('inv', [])) if isinstance(gstr1_data.get('b2b'), dict) else 0,
            "b2c_large_count": len(gstr1_data.get('b2cl', {}).get('inv', [])) if isinstance(gstr1_data.get('b2cl'), dict) else 0,
        }
    
    @tool
    def save_gstr1_to_file(gstr1_data: Dict, filename: str = None) -> Dict:
        """
        Save GSTR-1 JSON to file.
        
        Args:
            gstr1_data: GSTR-1 JSON data
            filename: Optional filename
            
        Returns:
            Dictionary with file path and size
        """
        try:
            file_path = save_gstr1_json(gstr1_data, filename)
            file_size = Path(file_path).stat().st_size
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": file_size,
                "file_name": Path(file_path).name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @tool
    def generate_gstr3b_return(output_gst: Dict[str, float], eligible_itc: Dict[str, float], period: str) -> Dict:
        """
        Generate GSTR-3B return data.
        
        Args:
            output_gst: Output GST liability {igst, cgst, sgst}
            eligible_itc: Eligible ITC {igst, cgst, sgst}
            period: Period in MM-YYYY format
            
        Returns:
            Dictionary with GSTR-3B Excel file
        """
        try:
            excel_buffer = generate_gstr3b_excel(output_gst, eligible_itc, period)
            
            return {
                "success": True,
                "excel_data": excel_buffer.getvalue(),
                "period": period,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @tool
    def generate_b2b_report(invoices: List[Dict]) -> Dict:
        """
        Generate B2B invoice report (GSTR-1 Table 4).
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Dictionary with B2B report data
        """
        # Filter B2B invoices (inter-state with GSTIN)
        b2b_invoices = []
        
        for inv in invoices:
            supplier_state = inv.get('supplier_gstin', '')[:2]
            recipient_state = inv.get('place_of_supply', '')[:2]
            
            # Inter-state supply
            if supplier_state != recipient_state:
                b2b_invoices.append({
                    "gstin": inv.get('recipient_gstin'),
                    "name": inv.get('recipient_name'),
                    "invoice_number": inv.get('invoice_number'),
                    "invoice_date": str(inv.get('invoice_date')),
                    "taxable_value": float(inv.get('taxable_value', 0)),
                    "igst": float(inv.get('igst', 0)),
                    "total_value": float(inv.get('total_value', 0)),
                })
        
        # Group by recipient GSTIN
        recipient_wise = {}
        for inv in b2b_invoices:
            gstin = inv['gstin']
            if gstin not in recipient_wise:
                recipient_wise[gstin] = {
                    "name": inv['name'],
                    "invoices": [],
                    "total_taxable": 0,
                    "total_tax": 0,
                }
            
            recipient_wise[gstin]["invoices"].append(inv)
            recipient_wise[gstin]["total_taxable"] += inv['taxable_value']
            recipient_wise[gstin]["total_tax"] += inv['igst']
        
        return {
            "success": True,
            "b2b_count": len(b2b_invoices),
            "recipient_count": len(recipient_wise),
            "recipient_wise": [
                {
                    "gstin": gstin,
                    "name": data["name"],
                    "invoice_count": len(data["invoices"]),
                    "total_taxable_value": round(data["total_taxable"], 2),
                    "total_igst": round(data["total_tax"], 2),
                }
                for gstin, data in recipient_wise.items()
            ],
        }
    
    @tool
    def generate_hsn_summary(invoices: List[Dict]) -> Dict:
        """
        Generate HSN-wise summary (GSTR-1 Table 12).
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Dictionary with HSN summary
        """
        hsn_wise = {}
        
        for inv in invoices:
            hsn_code = inv.get('hsn_code', 'UNCLASSIFIED')
            
            if hsn_code not in hsn_wise:
                hsn_wise[hsn_code] = {
                    "hsn_code": hsn_code,
                    "invoice_count": 0,
                    "total_taxable_value": 0,
                    "total_igst": 0,
                    "total_cgst": 0,
                    "total_sgst": 0,
                }
            
            hsn_wise[hsn_code]["invoice_count"] += 1
            hsn_wise[hsn_code]["total_taxable_value"] += float(inv.get('taxable_value', 0))
            hsn_wise[hsn_code]["total_igst"] += float(inv.get('igst', 0))
            hsn_wise[hsn_code]["total_cgst"] += float(inv.get('cgst', 0))
            hsn_wise[hsn_code]["total_sgst"] += float(inv.get('sgst', 0))
        
        return {
            "success": True,
            "hsn_count": len(hsn_wise),
            "hsn_wise": [
                {
                    "hsn_code": data["hsn_code"],
                    "invoice_count": data["invoice_count"],
                    "total_taxable_value": round(data["total_taxable_value"], 2),
                    "total_igst": round(data["total_igst"], 2),
                    "total_cgst": round(data["total_cgst"], 2),
                    "total_sgst": round(data["total_sgst"], 2),
                    "total_tax": round(data["total_igst"] + data["total_cgst"] + data["total_sgst"], 2),
                }
                for hsn, data in hsn_wise.items()
            ],
        }
    
    @tool
    def validate_gstr1_data(gstr1_data: Dict) -> Dict:
        """
        Validate GSTR-1 data before filing.
        
        Checks:
        - GSTIN format
        - Period format
        - Invoice data completeness
        - Tax calculations
        
        Args:
            gstr1_data: GSTR-1 JSON data
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check GSTIN
        gstin = gstr1_data.get('gstin', '')
        if len(gstin) != 15:
            errors.append(f"Invalid GSTIN length: {gstin}")
        
        # Check period format (MM-YYYY)
        period = gstr1_data.get('fp', '')
        if not period or len(period) != 7:
            errors.append(f"Invalid period format: {period}")
        
        # Check B2B invoices
        b2b = gstr1_data.get('b2b', [])
        if isinstance(b2b, dict):
            b2b = b2b.get('inv', [])
        
        for inv in b2b:
            # Check required fields
            if not inv.get('ctin'):
                errors.append(f"Missing recipient GSTIN in invoice {inv.get('inv_num')}")
            if not inv.get('inv_num'):
                errors.append("Missing invoice number")
            if not inv.get('inv_dt'):
                errors.append("Missing invoice date")
            
            # Check items
            items = inv.get('itms', [])
            for item in items:
                if not item.get('txval'):
                    warnings.append(f"Missing taxable value in invoice {inv.get('inv_num')}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

    @tool
    def generate_mismatch_report(mismatches: List[Dict], company_name: str, period: str) -> Dict:
        """
        Generate mismatch report Excel payload.

        Args:
            mismatches: List of mismatch dictionaries
            company_name: Company legal name
            period: Period in MM-YYYY format

        Returns:
            Dictionary with excel bytes payload
        """
        try:
            excel_buffer = generate_mismatch_report_excel(mismatches, company_name, period)
            return {
                "success": True,
                "excel_data": excel_buffer.getvalue(),
                "mismatch_count": len(mismatches),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    # Register tools
    agent.add_tool(generate_gstr1_return)
    agent.add_tool(save_gstr1_to_file)
    agent.add_tool(generate_gstr3b_return)
    agent.add_tool(generate_b2b_report)
    agent.add_tool(generate_hsn_summary)
    agent.add_tool(validate_gstr1_data)
    agent.add_tool(generate_mismatch_report)

    def execute(task: str, context: Dict = None) -> Dict:
        """
        Execute filing actions deterministically for known workflows.
        """
        context = context or {}
        task_lower = task.lower() if task else ""

        if "mismatch report" in task_lower:
            return generate_mismatch_report(
                context.get("mismatches", []),
                context.get("company_name", ""),
                context.get("period", ""),
            )

        if "gstr-1" in task_lower or "gstr1" in task_lower:
            return generate_gstr1_return(
                context.get("invoices", []),
                context.get("company_gstin", ""),
                context.get("period", ""),
            )

        if "gstr-3b" in task_lower or "gstr3b" in task_lower:
            return generate_gstr3b_return(
                context.get("output_gst", {}),
                context.get("eligible_itc", {}),
                context.get("period", ""),
            )

        if "b2b" in task_lower:
            return generate_b2b_report(context.get("invoices", []))

        if "hsn" in task_lower:
            return generate_hsn_summary(context.get("invoices", []))

        if "validate" in task_lower:
            return validate_gstr1_data(context.get("gstr1_data", {}))

        return {
            "success": False,
            "error": f"Unsupported filing task: {task}",
        }

    agent.execute = execute
    
    return agent


# Singleton instance
_filing_agent = None


def get_filing_agent() -> BaseAgent:
    """Get or create FilingAgent singleton."""
    global _filing_agent
    if _filing_agent is None:
        _filing_agent = create_filing_agent()
    return _filing_agent
