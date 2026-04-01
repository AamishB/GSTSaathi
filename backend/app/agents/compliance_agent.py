"""
ComplianceAgent for ITC calculation and GST compliance rules.
Uses smolagents CodeAgent with ITC calculation tools.
"""
from typing import Dict, List, Any
from decimal import Decimal, ROUND_HALF_UP

from .base_agent import BaseAgent
from ..utils.itc_calculator import (
    calculate_itc_on_invoice,
    apply_section_17_5_blocked_credits,
    calculate_net_gst_payable,
)


def create_compliance_agent() -> BaseAgent:
    """
    Create ComplianceAgent with all compliance calculation tools.
    
    Returns:
        Configured ComplianceAgent
    """
    from smolagents import tool
    
    agent = BaseAgent(
        name="ComplianceAgent",
        description="Calculates eligible ITC, applies Section 17(5), determines net GST payable",
    )
    
    @tool
    def calculate_eligible_itc(matched_invoices: List[Dict], blocked_categories: List[str] = None) -> Dict:
        """
        Calculate eligible Input Tax Credit from matched invoices.
        
        Args:
            matched_invoices: List of matched invoice dictionaries
            blocked_categories: Optional list of Section 17(5) blocked categories
            
        Returns:
            Dictionary with eligible ITC breakdown
        """
        total_igst = 0
        total_cgst = 0
        total_sgst = 0
        total_taxable = 0
        
        for invoice in matched_invoices:
            # Check if ITC is eligible for this invoice
            itc_eligible = invoice.get('itc_eligible', True)
            
            if itc_eligible:
                total_igst += float(invoice.get('igst', 0))
                total_cgst += float(invoice.get('cgst', 0))
                total_sgst += float(invoice.get('sgst', 0))
                total_taxable += float(invoice.get('taxable_value', 0))
        
        total_itc = total_igst + total_cgst + total_sgst
        
        # Apply Section 17(5) blocked credits if specified
        if blocked_categories:
            blocked_result = apply_section_17_5_blocked_credits(total_itc, blocked_categories)
            eligible_itc = blocked_result['eligible_itc']
            blocked_itc = blocked_result['blocked_itc']
        else:
            eligible_itc = total_itc
            blocked_itc = 0
        
        return {
            "total_itc": round(total_itc, 2),
            "eligible_itc": round(eligible_itc, 2),
            "blocked_itc": round(blocked_itc, 2),
            "breakdown": {
                "igst": round(total_igst, 2),
                "cgst": round(total_cgst, 2),
                "sgst": round(total_sgst, 2),
            },
            "taxable_value": round(total_taxable, 2),
        }
    
    @tool
    def calculate_itc_at_risk(missing_invoices: List[Dict]) -> Dict:
        """
        Calculate ITC at risk from invoices missing in GSTR-2B.
        
        Args:
            missing_invoices: List of invoices missing in GSTR-2B
            
        Returns:
            Dictionary with ITC at risk calculation
        """
        total_taxable_value = 0
        total_tax_amount = 0
        
        for invoice in missing_invoices:
            total_taxable_value += float(invoice.get('taxable_value', 0))
            total_tax_amount += (
                float(invoice.get('igst', 0)) +
                float(invoice.get('cgst', 0)) +
                float(invoice.get('sgst', 0))
            )
        
        # Group by supplier for vendor-wise risk analysis
        supplier_risk = {}
        for invoice in missing_invoices:
            supplier_gstin = invoice.get('supplier_gstin', 'Unknown')
            if supplier_gstin not in supplier_risk:
                supplier_risk[supplier_gstin] = {
                    "supplier_name": invoice.get('supplier_name', 'Unknown'),
                    "invoice_count": 0,
                    "taxable_value": 0,
                    "tax_amount": 0,
                }
            
            supplier_risk[supplier_gstin]["invoice_count"] += 1
            supplier_risk[supplier_gstin]["taxable_value"] += float(invoice.get('taxable_value', 0))
            supplier_risk[supplier_gstin]["tax_amount"] += (
                float(invoice.get('igst', 0)) +
                float(invoice.get('cgst', 0)) +
                float(invoice.get('sgst', 0))
            )
        
        return {
            "total_itc_at_risk": round(total_tax_amount, 2),
            "total_taxable_value": round(total_taxable_value, 2),
            "invoice_count": len(missing_invoices),
            "supplier_wise_breakdown": [
                {
                    "supplier_gstin": gstin,
                    "supplier_name": data["supplier_name"],
                    "invoice_count": data["invoice_count"],
                    "taxable_value": round(data["taxable_value"], 2),
                    "tax_amount": round(data["tax_amount"], 2),
                }
                for gstin, data in sorted(supplier_risk.items(), key=lambda x: x[1]["tax_amount"], reverse=True)[:10]
            ],
        }
    
    @tool
    def calculate_net_gst_liability(output_gst: Dict[str, float], eligible_itc: Dict[str, float]) -> Dict:
        """
        Calculate net GST payable after ITC set-off.
        
        ITC set-off order:
        1. IGST ITC → IGST liability → CGST liability → SGST liability
        2. CGST ITC → CGST liability → IGST liability (not SGST)
        3. SGST ITC → SGST liability → IGST liability (not CGST)
        
        Args:
            output_gst: Output GST liability {igst, cgst, sgst}
            eligible_itc: Eligible ITC {igst, cgst, sgst}
            
        Returns:
            Dictionary with net GST payable and utilization details
        """
        return calculate_net_gst_payable(output_gst, eligible_itc)
    
    @tool
    def check_section_17_5(invoice: Dict) -> Dict:
        """
        Check if invoice falls under Section 17(5) blocked credits.
        
        Section 17(5) blocked categories:
        - Motor vehicles for passenger transport
        - Food and beverages, outdoor catering
        - Beauty treatment, health services
        - Club membership, health & fitness centre
        - Travel benefits to employees
        - Personal use goods/services
        - Free samples, gifts
        
        Args:
            invoice: Invoice dictionary
            
        Returns:
            Dictionary with blocked credit determination
        """
        # Get HSN code
        hsn_code = invoice.get('hsn_code', '')
        description = invoice.get('description', '').lower()
        
        blocked_categories = []
        
        # Check HSN chapters for blocked items
        if hsn_code:
            hsn_chapter = hsn_code[:2]
            
            # Chapter 87: Motor vehicles
            if hsn_chapter == '87':
                blocked_categories.append('motor_vehicles')
            
            # Chapter 21, 22: Food and beverages
            elif hsn_chapter in ['21', '22']:
                blocked_categories.append('food_beverages')
        
        # Check description for keywords
        blocked_keywords = [
            ('car', 'motor_vehicles'),
            ('vehicle', 'motor_vehicles'),
            ('catering', 'food_beverages'),
            ('restaurant', 'food_beverages'),
            ('hotel', 'food_beverages'),
            ('membership', 'club_membership'),
            ('travel', 'travel_benefits'),
            ('gift', 'free_samples'),
            ('sample', 'free_samples'),
        ]
        
        for keyword, category in blocked_keywords:
            if keyword in description:
                blocked_categories.append(category)
        
        # Remove duplicates
        blocked_categories = list(set(blocked_categories))
        
        is_blocked = len(blocked_categories) > 0
        
        return {
            "is_blocked": is_blocked,
            "blocked_categories": blocked_categories,
            "itc_eligible": not is_blocked,
            "reason": f"Blocked under Section 17(5): {', '.join(blocked_categories)}" if is_blocked else "Not blocked",
        }
    
    # Register tools
    agent.add_tool(calculate_eligible_itc)
    agent.add_tool(calculate_itc_at_risk)
    agent.add_tool(calculate_net_gst_liability)
    agent.add_tool(check_section_17_5)
    
    return agent


# Singleton instance
_compliance_agent = None


def get_compliance_agent() -> BaseAgent:
    """Get or create ComplianceAgent singleton."""
    global _compliance_agent
    if _compliance_agent is None:
        _compliance_agent = create_compliance_agent()
    return _compliance_agent
