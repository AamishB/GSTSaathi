"""
ITC (Input Tax Credit) calculator.
Implements GST rules for eligible ITC calculation including Section 17(5) blocked credits.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class ITCComponent:
    """Represents a component of ITC."""
    taxable_value: Decimal
    igst: Decimal
    cgst: Decimal
    sgst: Decimal
    is_eligible: bool
    ineligible_reason: Optional[str] = None


# Section 17(5) blocked credit categories
BLOCKED_CREDIT_CATEGORIES = {
    "motor_vehicles": "Motor vehicles for transportation of persons (≤13 persons)",
    "food_beverages": "Food and beverages, outdoor catering",
    "beauty_treatment": "Beauty treatment, health services, cosmetic surgery",
    "club_membership": "Membership of club, health and fitness centre",
    "travel_benefits": "Travel benefits to employees",
    "composition_scheme": "Goods/services used for composition scheme",
    "lost_stolen": "Lost, stolen, destroyed goods/services",
    "personal_use": "Goods/services for personal use",
    "free_samples": "Free samples, gifts",
    "fraud_default": "Supplier fraud/default",
}


def calculate_itc_on_invoice(
    taxable_value: float,
    igst: float,
    cgst: float,
    sgst: float,
    is_inter_state: bool = False,
) -> Dict:
    """
    Calculate ITC for a single invoice.
    
    Args:
        taxable_value: Taxable value of invoice
        igst: IGST amount
        cgst: CGST amount
        sgst: SGST amount
        is_inter_state: True if inter-state supply
        
    Returns:
        Dictionary with ITC breakdown
    """
    # Validate tax amounts
    total_tax = igst + cgst + sgst
    
    # For inter-state, only IGST applies
    if is_inter_state and (cgst > 0 or sgst > 0):
        return {
            "valid": False,
            "error": "Inter-state invoice should only have IGST",
            "itc": {"igst": 0, "cgst": 0, "sgst": 0, "total": 0},
        }
    
    # For intra-state, CGST + SGST applies (no IGST)
    if not is_inter_state and igst > 0:
        return {
            "valid": False,
            "error": "Intra-state invoice should only have CGST and SGST",
            "itc": {"igst": 0, "cgst": 0, "sgst": 0, "total": 0},
        }
    
    return {
        "valid": True,
        "itc": {
            "igst": igst,
            "cgst": cgst,
            "sgst": sgst,
            "total": total_tax,
        },
        "taxable_value": taxable_value,
    }


def apply_section_17_5_blocked_credits(
    itc_amount: float,
    blocked_categories: List[str],
) -> Dict:
    """
    Apply Section 17(5) blocked credit rules.
    
    Section 17(5) specifies expenses where ITC is not available:
    - Motor vehicles for passenger transport (≤13 persons)
    - Food and beverages, outdoor catering
    - Beauty treatment, health services
    - Club membership, health & fitness centre
    - Travel benefits to employees
    - Composition scheme supplies
    - Lost, stolen, destroyed goods
    - Personal use goods/services
    - Free samples, gifts
    - Supplier fraud/default
    
    Args:
        itc_amount: Total ITC amount
        blocked_categories: List of blocked credit category codes
        
    Returns:
        Dictionary with eligible and blocked ITC amounts
    """
    if not blocked_categories:
        return {
            "total_itc": itc_amount,
            "blocked_itc": 0,
            "eligible_itc": itc_amount,
            "blocked_categories": [],
        }
    
    # For MVP, we block entire ITC if any blocked category applies
    # In production, this would be more granular
    blocked_amount = itc_amount if blocked_categories else 0
    eligible_amount = 0 if blocked_categories else itc_amount
    
    blocked_details = [
        {"category": cat, "description": BLOCKED_CREDIT_CATEGORIES.get(cat, "Unknown")}
        for cat in blocked_categories
    ]
    
    return {
        "total_itc": itc_amount,
        "blocked_itc": blocked_amount,
        "eligible_itc": eligible_amount,
        "blocked_categories": blocked_details,
    }


def calculate_net_gst_payable(
    output_gst: Dict[str, float],
    eligible_itc: Dict[str, float],
) -> Dict:
    """
    Calculate net GST payable after ITC set-off.
    
    ITC set-off order as per GST rules:
    1. IGST ITC → IGST liability → CGST liability → SGST liability
    2. CGST ITC → CGST liability → IGST liability (not SGST)
    3. SGST ITC → SGST liability → IGST liability (not CGST)
    
    Args:
        output_gst: Output GST liability {igst, cgst, sgst}
        eligible_itc: Eligible ITC {igst, cgst, sgst}
        
    Returns:
        Dictionary with net GST payable and ITC utilization
    """
    # Initialize
    igst_liability = Decimal(str(output_gst.get("igst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    cgst_liability = Decimal(str(output_gst.get("cgst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sgst_liability = Decimal(str(output_gst.get("sgst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    igst_itc = Decimal(str(eligible_itc.get("igst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    cgst_itc = Decimal(str(eligible_itc.get("cgst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sgst_itc = Decimal(str(eligible_itc.get("sgst", 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Step 1: IGST ITC set-off
    # First against IGST liability
    igst_utilized = min(igst_itc, igst_liability)
    igst_liability -= igst_utilized
    igst_itc -= igst_utilized
    
    # Then against CGST liability
    cgst_from_igst = min(igst_itc, cgst_liability)
    cgst_liability -= cgst_from_igst
    igst_itc -= cgst_from_igst
    
    # Then against SGST liability
    sgst_from_igst = min(igst_itc, sgst_liability)
    sgst_liability -= sgst_from_igst
    igst_itc -= sgst_from_igst
    
    # Step 2: CGST ITC set-off
    # First against CGST liability
    cgst_utilized = min(cgst_itc, cgst_liability)
    cgst_liability -= cgst_utilized
    cgst_itc -= cgst_utilized
    
    # Then against IGST liability (not SGST)
    igst_from_cgst = min(cgst_itc, igst_liability)
    igst_liability -= igst_from_cgst
    cgst_itc -= igst_from_cgst
    
    # Step 3: SGST ITC set-off
    # First against SGST liability
    sgst_utilized = min(sgst_itc, sgst_liability)
    sgst_liability -= sgst_utilized
    sgst_itc -= sgst_utilized
    
    # Then against IGST liability (not CGST)
    igst_from_sgst = min(sgst_itc, igst_liability)
    igst_liability -= igst_from_sgst
    sgst_itc -= igst_from_sgst
    
    # Calculate totals
    net_gst_payable = float(igst_liability + cgst_liability + sgst_liability)
    total_itc_utilized = (
        float(igst_itc - Decimal(str(eligible_itc.get("igst", 0)))) +
        float(cgst_itc - Decimal(str(eligible_itc.get("cgst", 0)))) +
        float(sgst_itc - Decimal(str(eligible_itc.get("sgst", 0))))
    )
    
    # Unutilized ITC (carried forward)
    unutilized_itc = {
        "igst": float(igst_itc),
        "cgst": float(cgst_itc),
        "sgst": float(sgst_itc),
        "total": float(igst_itc + cgst_itc + sgst_itc),
    }
    
    return {
        "net_gst_payable": net_gst_payable,
        "breakdown": {
            "igst_payable": float(igst_liability),
            "cgst_payable": float(cgst_liability),
            "sgst_payable": float(sgst_liability),
        },
        "itc_utilized": {
            "igst": float(Decimal(str(eligible_itc.get("igst", 0))) - igst_itc),
            "cgst": float(Decimal(str(eligible_itc.get("cgst", 0))) - cgst_itc),
            "sgst": float(Decimal(str(eligible_itc.get("sgst", 0))) - sgst_itc),
            "total": total_itc_utilized,
        },
        "unutilized_itc": unutilized_itc,
    }


def calculate_interest_on_delayed_payment(
    tax_amount: float,
    due_date: str,
    payment_date: str,
    rate: float = 18.0,
) -> Dict:
    """
    Calculate interest on delayed GST payment.
    
    Interest rate:
    - 18% per annum for delayed payment
    - 24% per annum for ineligible ITC claimed
    
    Args:
        tax_amount: Tax amount delayed
        due_date: Due date (YYYY-MM-DD)
        payment_date: Payment date (YYYY-MM-DD)
        rate: Interest rate (default 18%)
        
    Returns:
        Dictionary with interest calculation
    """
    from datetime import datetime
    
    due = datetime.strptime(due_date, "%Y-%m-%d")
    paid = datetime.strptime(payment_date, "%Y-%m-%d")
    
    delay_days = (paid - due).days
    
    if delay_days <= 0:
        return {
            "interest": 0,
            "delay_days": 0,
            "is_delayed": False,
        }
    
    # Interest = Tax × Rate × Days / 365
    interest = (tax_amount * rate * delay_days) / 365
    
    return {
        "interest": round(interest, 2),
        "delay_days": delay_days,
        "is_delayed": True,
        "rate": rate,
    }
