"""
Mismatch Agent - Compares invoices with GSTR-2A data
Updated for smolagents 1.24.0
"""
import pandas as pd
import json
from typing import List, Dict, Any
from smolagents import Tool


class GSTR2AComparator(Tool):
    """Compare purchase invoices with GSTR-2A auto-populated data"""
    name = "gstr2a_comparator"
    description = "Compares purchase invoices with GSTR-2A data to find mismatches and missing invoices"
    inputs = {
        "purchase_invoices": {"type": "any", "description": "List of purchase invoices from books"},
        "gstr2a_data": {"type": "any", "description": "List of invoices from GSTR-2A"}
    }
    output_type = "any"
    
    def forward(self, purchase_invoices: Any, gstr2a_data: Any) -> Any:
        """
        Compare invoices and categorize into:
        - Matched: Invoice found in both books and GSTR-2A with same values
        - Mismatch: Invoice found in both but values differ
        - Missing: Invoice in books but not in GSTR-2A (ITC at risk)
        """
        try:
            # Convert to DataFrames
            df_books = pd.DataFrame(purchase_invoices)
            df_gstr2a = pd.DataFrame(gstr2a_data)
            
            mismatches = []
            matched_count = 0
            
            # Group by GSTIN for comparison
            for _, book_invoice in df_books.iterrows():
                vendor_gstin = book_invoice.get('vendor_gstin', '')
                invoice_number = book_invoice.get('invoice_number', '')
                book_amount = float(book_invoice.get('total_value', 0))
                
                # Find matching invoice in GSTR-2A
                gstr2a_match = df_gstr2a[
                    (df_gstr2a['vendor_gstin'] == vendor_gstin) & 
                    (df_gstr2a['invoice_number'] == invoice_number)
                ]
                
                if len(gstr2a_match) == 0:
                    # Invoice missing in GSTR-2A
                    mismatches.append({
                        "vendor_name": book_invoice.get('vendor_name', 'Unknown'),
                        "vendor_gstin": vendor_gstin,
                        "invoice_number": invoice_number,
                        "invoice_date": book_invoice.get('invoice_date', ''),
                        "our_record_amount": book_amount,
                        "gstr2a_amount": None,
                        "status": "missing",
                        "difference": book_amount,
                        "tax_at_risk": float(book_invoice.get('cgst', 0) + book_invoice.get('sgst', 0) + book_invoice.get('igst', 0))
                    })
                else:
                    gstr2a_invoice = gstr2a_match.iloc[0]
                    gstr2a_amount = float(gstr2a_invoice.get('total_value', 0))
                    
                    # Check if amounts match (within 1 rupee tolerance)
                    if abs(book_amount - gstr2a_amount) > 1.0:
                        # Amount mismatch
                        mismatches.append({
                            "vendor_name": book_invoice.get('vendor_name', 'Unknown'),
                            "vendor_gstin": vendor_gstin,
                            "invoice_number": invoice_number,
                            "invoice_date": book_invoice.get('invoice_date', ''),
                            "our_record_amount": book_amount,
                            "gstr2a_amount": gstr2a_amount,
                            "status": "mismatch",
                            "difference": book_amount - gstr2a_amount,
                            "tax_at_risk": abs(float(book_invoice.get('cgst', 0) + book_invoice.get('sgst', 0) + book_invoice.get('igst', 0)) - 
                                            float(gstr2a_invoice.get('cgst', 0) + gstr2a_invoice.get('sgst', 0) + gstr2a_invoice.get('igst', 0)))
                        })
                    else:
                        matched_count += 1
            
            # Calculate ITC at risk
            itc_at_risk = sum(m.get('tax_at_risk', 0) for m in mismatches)
            
            return {
                "success": True,
                "matched_count": matched_count,
                "mismatch_count": len([m for m in mismatches if m['status'] == 'mismatch']),
                "missing_count": len([m for m in mismatches if m['status'] == 'missing']),
                "total_mismatches": len(mismatches),
                "itc_at_risk": itc_at_risk,
                "mismatches": mismatches
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "matched_count": 0,
                "mismatch_count": 0,
                "missing_count": 0,
                "total_mismatches": 0,
                "itc_at_risk": 0,
                "mismatches": []
            }


def analyze_mismatches(purchase_invoices: List[Dict], gstr2a_data: List[Dict]) -> Dict:
    """
    Analyze mismatches between purchase invoices and GSTR-2A data
    Uses pandas-based comparison (simplified approach without LLM call for speed)
    """
    try:
        comparator = GSTR2AComparator()
        result = comparator.forward(purchase_invoices, gstr2a_data)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "matched_count": 0,
            "mismatch_count": 0,
            "missing_count": 0,
            "total_mismatches": 0,
            "itc_at_risk": 0,
            "mismatches": []
        }
