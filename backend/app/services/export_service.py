"""
Export service for generating GST return files (GSTR-1, GSTR-3B).
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session
from openpyxl import Workbook

from ..models.invoice import Invoice
from ..models.reconciliation import ReconciliationResult
from ..config import settings


def generate_gstr1_json(
    invoices: List[Invoice],
    company_gstin: str,
    period: str,  # MM-YYYY
) -> Dict:
    """
    Generate GSTR-1 JSON in GSTN offline tool format.
    
    Args:
        invoices: List of invoices for the period
        company_gstin: Company GSTIN
        period: Period in MM-YYYY format
        
    Returns:
        Dictionary in GSTN GSTR-1 JSON format
    """
    # Group invoices by type (B2B, B2C Large, B2C Small)
    b2b_invoices = []
    b2c_large_invoices = []
    b2c_small_invoices = []
    
    for invoice in invoices:
        # Determine invoice type based on value and recipient
        invoice_value = invoice.total_value
        is_inter_state = invoice.place_of_supply[:2] != company_gstin[:2]
        
        # B2B: All inter-state supplies to registered persons
        # For MVP, assume all with GSTIN are registered
        if is_inter_state:
            b2b_invoices.append({
                "ctin": invoice.recipient_gstin,
                "inv_num": invoice.invoice_number,
                "inv_dt": invoice.invoice_date.strftime("%d-%m-%Y"),
                "inv_val": round(invoice.taxable_value, 2),
                "pos": invoice.place_of_supply,
                "rchrg": "N",  # Reverse charge - assume no
                "inv_typ": "R",  # Regular
                "itms": [
                    {
                        "num": 1,
                        "txval": round(invoice.taxable_value, 2),
                        "rt": get_gst_rate(invoice.taxable_value, invoice.igst + invoice.cgst + invoice.sgst),
                        "iamt": round(invoice.igst, 2),
                        "camt": round(invoice.cgst, 2),
                        "samt": round(invoice.sgst, 2),
                    }
                ],
            })
        elif invoice_value > 250000:  # B2C Large (> ₹2.5L)
            b2c_large_invoices.append({
                "inv_num": invoice.invoice_number,
                "inv_dt": invoice.invoice_date.strftime("%d-%m-%Y"),
                "inv_val": round(invoice.taxable_value, 2),
                "pos": invoice.place_of_supply,
                "itms": [
                    {
                        "num": 1,
                        "txval": round(invoice.taxable_value, 2),
                        "rt": get_gst_rate(invoice.taxable_value, invoice.igst + invoice.cgst + invoice.sgst),
                        "iamt": round(invoice.igst, 2),
                        "camt": round(invoice.cgst, 2),
                        "samt": round(invoice.sgst, 2),
                    }
                ],
            })
        else:  # B2C Small
            # Aggregate by place of supply and tax rate
            b2c_small_invoices.append(invoice)
    
    # Aggregate B2C small invoices
    b2c_small_aggregated = aggregate_b2c_small(b2c_small_invoices)
    
    # Build GSTR-1 JSON structure
    gstr1_data = {
        "gstin": company_gstin,
        "fp": period,  # Financial period
        "gt": round(sum(inv.total_value for inv in invoices), 2),  # Gross turnover
        "cur_gt": round(sum(inv.total_value for inv in invoices), 2),
        "b2b": {
            "csup_typ": "R",
            "inv": b2b_invoices,
        } if b2b_invoices else [],
        "b2cl": {
            "csup_typ": "R",
            "inv": b2c_large_invoices,
        } if b2c_large_invoices else [],
        "b2cs": b2c_small_aggregated,
        "version": "1.0",
        "generated_on": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }
    
    return gstr1_data


def get_gst_rate(taxable_value: float, tax_amount: float) -> float:
    """
    Calculate GST rate percentage from taxable value and tax amount.
    
    Args:
        taxable_value: Taxable value
        tax_amount: Total tax amount
        
    Returns:
        GST rate percentage (0, 5, 12, 18, or 28)
    """
    if taxable_value == 0:
        return 0.0
    
    rate = (tax_amount / taxable_value) * 100
    
    # Round to nearest standard rate
    standard_rates = [0, 5, 12, 18, 28]
    return min(standard_rates, key=lambda x: abs(x - rate))


def aggregate_b2c_small(invoices: List[Invoice]) -> List[Dict]:
    """
    Aggregate B2C small invoices by place of supply and tax rate.
    
    Args:
        invoices: List of B2C small invoices
        
    Returns:
        List of aggregated invoice records
    """
    if not invoices:
        return []
    
    # Group by place of supply and tax rate
    aggregated = {}
    
    for invoice in invoices:
        key = (invoice.place_of_supply, get_gst_rate(invoice.taxable_value, invoice.igst + invoice.cgst + invoice.sgst))
        
        if key not in aggregated:
            aggregated[key] = {
                "pos": invoice.place_of_supply,
                "rt": key[1],
                "txval": 0,
                "iamt": 0,
                "camt": 0,
                "samt": 0,
            }
        
        aggregated[key]["txval"] += invoice.taxable_value
        aggregated[key]["iamt"] += invoice.igst
        aggregated[key]["camt"] += invoice.cgst
        aggregated[key]["samt"] += invoice.sgst
    
    # Round values
    result = []
    for data in aggregated.values():
        result.append({
            "pos": data["pos"],
            "rt": data["rt"],
            "txval": round(data["txval"], 2),
            "iamt": round(data["iamt"], 2),
            "camt": round(data["camt"], 2),
            "samt": round(data["samt"], 2),
        })
    
    return result


def save_gstr1_json(data: Dict, filename: Optional[str] = None) -> str:
    """
    Save GSTR-1 JSON to file.
    
    Args:
        data: GSTR-1 JSON data
        filename: Optional filename
        
    Returns:
        Path to saved file
    """
    export_dir = Path(settings.EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"GSTR1_{timestamp}.json"
    
    file_path = export_dir / filename
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(file_path)


def generate_gstr3b_excel(
    output_gst: Dict[str, float],
    eligible_itc: Dict[str, float],
    period: str,  # MM-YYYY
) -> BytesIO:
    """
    Generate GSTR-3B Excel file.
    
    Args:
        output_gst: Output GST {igst, cgst, sgst}
        eligible_itc: Eligible ITC {igst, cgst, sgst}
        period: Period in MM-YYYY format
        
    Returns:
        BytesIO object with Excel file
    """
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "GSTR-3B"
    
    # Header
    ws.append(["GSTR-3B Summary Return"])
    ws.append([f"Period: {period}"])
    ws.append([])
    
    # Table 3.1 - Outward Supplies
    ws.append(["Table 3.1: Details of Outward Supplies and Inward Supplies liable to Reverse Charge"])
    ws.append(["Nature of Supplies", "Total Taxable Value", "Integrated Tax", "Central Tax", "State/UT Tax"])
    
    output_total = output_gst.get("igst", 0) + output_gst.get("cgst", 0) + output_gst.get("sgst", 0)
    ws.append([
        "Outward taxable supplies",
        round(output_total, 2),
        round(output_gst.get("igst", 0), 2),
        round(output_gst.get("cgst", 0), 2),
        round(output_gst.get("sgst", 0), 2),
    ])
    ws.append([])
    
    # Table 4 - Eligible ITC
    ws.append(["Table 4: Eligible ITC"])
    ws.append(["Details", "Integrated tax", "Central tax", "State/UT tax", "Total"])
    
    itc_total = eligible_itc.get("igst", 0) + eligible_itc.get("cgst", 0) + eligible_itc.get("sgst", 0)
    ws.append([
        "All other ITC",
        round(eligible_itc.get("igst", 0), 2),
        round(eligible_itc.get("cgst", 0), 2),
        round(eligible_itc.get("sgst", 0), 2),
        round(itc_total, 2),
    ])
    ws.append([])
    
    # Table 5.1 - Interest and Late Fee
    ws.append(["Table 5.1: Interest and Late Fee"])
    ws.append(["Description", "Integrated tax", "Central tax", "State/UT tax", "Total"])
    ws.append(["Interest", 0, 0, 0, 0])
    ws.append(["Late fee", 0, 0, 0, 0])
    ws.append([])
    
    # Tax Payable
    ws.append(["Tax Payable"])
    ws.append([
        "Net GST Payable",
        round(max(0, output_gst.get("igst", 0) - eligible_itc.get("igst", 0)), 2),
        round(max(0, output_gst.get("cgst", 0) - eligible_itc.get("cgst", 0)), 2),
        round(max(0, output_gst.get("sgst", 0) - eligible_itc.get("sgst", 0)), 2),
        round(
            max(0, output_gst.get("igst", 0) - eligible_itc.get("igst", 0)) +
            max(0, output_gst.get("cgst", 0) - eligible_itc.get("cgst", 0)) +
            max(0, output_gst.get("sgst", 0) - eligible_itc.get("sgst", 0)),
            2
        ),
    ])
    
    # Save to BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer


def generate_mismatch_report_excel(
    mismatches: List[Dict],
    company_name: str,
    period: str,
) -> BytesIO:
    """
    Generate mismatch report Excel file.
    
    Args:
        mismatches: List of mismatch records
        company_name: Company name
        period: Period in MM-YYYY format
        
    Returns:
        BytesIO object with Excel file
    """
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Mismatch Report"
    
    # Header
    ws.append(["GST Reconciliation - Mismatch Report"])
    ws.append([f"Company: {company_name}"])
    ws.append([f"Period: {period}"])
    ws.append([f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"])
    ws.append([])
    
    # Summary
    total_mismatches = len(mismatches)
    missing_count = sum(1 for m in mismatches if m.get('mismatch_type') == 'missing_in_gstr2b')
    value_diff_count = sum(1 for m in mismatches if m.get('mismatch_type') == 'value_mismatch')
    
    ws.append(["Summary"])
    ws.append(["Total Mismatches", total_mismatches])
    ws.append(["Missing in GSTR-2B", missing_count])
    ws.append(["Value Mismatch", value_diff_count])
    ws.append([])
    
    # Detailed table
    ws.append(["Detailed Mismatch Report"])
    headers = [
        "Invoice Number", "Invoice Date", "Supplier GSTIN", "Supplier Name",
        "Booked Taxable Value", "GSTR-2B Taxable Value", "Tax Difference",
        "Mismatch Type", "Action Taken"
    ]
    ws.append(headers)
    
    for m in mismatches:
        ws.append([
            m.get('invoice_number', ''),
            m.get('invoice_date', ''),
            m.get('supplier_gstin', ''),
            m.get('supplier_name', ''),
            round(m.get('booked_taxable_value', 0), 2),
            round(m.get('gstr2b_taxable_value', 0), 2) if m.get('gstr2b_taxable_value') else 'N/A',
            round(m.get('tax_difference', 0), 2),
            m.get('mismatch_type', ''),
            m.get('action_taken', 'pending'),
        ])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer
