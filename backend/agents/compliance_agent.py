"""
Compliance Auditor Agent - Risk Assessment Specialist
Identifies compliance risks and flags issues
"""
from typing import Dict, List, Any


class ComplianceAuditorAgent:
    """
    Specialist agent for compliance risk assessment
    Flags high-risk invoices and compliance issues
    """
    
    def __init__(self):
        self.risk_thresholds = {
            "high": 75,
            "medium": 50,
            "low": 25
        }
    
    async def audit(self, invoice_data: Dict, gstr2a_data: List) -> Dict:
        """
        Perform compliance audit on invoice data
        Returns risk assessment with flagged issues
        """
        # Mock audit logic (would use ML in production)
        total_invoices = len(invoice_data) if isinstance(invoice_data, list) else invoice_data.get('count', 0)
        
        # Calculate risk metrics
        mismatch_count = int(total_invoices * 0.12)  # 12% mismatch rate
        high_risk_count = int(total_invoices * 0.05)  # 5% high risk
        
        overall_risk_score = min(100, (mismatch_count / total_invoices * 100) * 2) if total_invoices > 0 else 0
        
        issues = []
        if mismatch_count > 5:
            issues.append({
                "type": "high_mismatch_rate",
                "severity": "high",
                "description": f"{mismatch_count} invoices have mismatches with GSTR-2A",
                "recommendation": "Review and reconcile before filing"
            })
        
        if high_risk_count > 2:
            issues.append({
                "type": "vendor_default_risk",
                "severity": "medium",
                "description": f"{high_risk_count} vendors have history of late filing",
                "recommendation": "Send reminders and follow up"
            })
        
        return {
            "total_audited": total_invoices,
            "risk_count": mismatch_count,
            "high_risk_count": high_risk_count,
            "overall_risk_score": int(overall_risk_score),
            "issues": issues,
            "recommendation": "address_issues" if overall_risk_score > 50 else "proceed_with_filing",
            "confidence": 0.82
        }
    
    async def opinion(self, topic: str, context: Dict) -> str:
        """Provide compliance opinion for agent debates"""
        if topic == "high_risk_invoices":
            risk_score = context[1].get('overall_risk_score', 50)
            if risk_score > 70:
                return f"⚠️ Compliance Alert: Risk score {risk_score}/100 exceeds threshold. Recommend excluding high-risk invoices and sending vendor notices before claiming ITC."
            else:
                return f"✓ Compliance Check: Risk score {risk_score}/100 is acceptable. Can proceed with ITC claim with proper documentation."
        
        elif topic == "vendor_default_risk":
            return "Recommendation: Implement vendor compliance scoring. Send automated reminders to high-risk vendors. Consider partial ITC claim for compliant invoices."
        
        return "Compliance review required for this scenario."


class FinanceOptimizerAgent:
    """
    Specialist agent for cash flow optimization
    Suggests optimal filing timing to maximize returns
    """
    
    def __init__(self):
        self.fd_rate = 0.07  # 7% annual return
        self.working_capital_cost = 0.12  # 12% cost of capital
    
    async def optimize(self, invoice_data: Dict) -> Dict:
        """
        Optimize filing timing for cash flow
        Returns optimal date and projected savings
        """
        # Calculate total GST payable
        total_sales = invoice_data.get('total_sales', 5000000)  # Default 50L
        gst_payable = total_sales * 0.18
        
        # Calculate optimal filing date
        today = __import__('datetime').datetime.now()
        due_date = today.replace(day=20)
        if due_date < today:
            # Next month
            due_date = due_date.replace(month=due_date.month + 1)
        
        optimal_date = due_date  # File on last possible date
        
        # Calculate interest savings
        days_delay = (due_date - today).days
        daily_interest = gst_payable * (self.fd_rate / 365)
        savings = daily_interest * days_delay
        
        return {
            "total_sales": total_sales,
            "gst_payable": gst_payable,
            "optimal_date": optimal_date.strftime("%Y-%m-%d"),
            "days_until_due": days_delay,
            "savings": int(savings),
            "roi_percentage": (savings / gst_payable * 100) if gst_payable > 0 else 0,
            "recommendation": "delay" if savings > 5000 else "file_now",
            "confidence": 0.91
        }
    
    async def opinion(self, topic: str, context: Dict) -> str:
        """Provide finance opinion for agent debates"""
        if topic == "filing_timing":
            finance_data = context[2]
            savings = finance_data.get('savings', 0)
            optimal_date = finance_data.get('optimal_date', '')
            
            if savings > 10000:
                return f"💰 Finance Recommendation: Delay filing to {optimal_date} to earn ₹{savings:,} additional interest. This is risk-free return on idle cash."
            elif savings > 5000:
                return f"💰 Finance Recommendation: Moderate savings of ₹{savings:,}. Consider delaying if compliance risk is low."
            else:
                return "💰 Finance Recommendation: Minimal interest savings. File immediately for peace of mind."
        
        elif topic == "high_risk_invoices":
            return "Financial impact of incorrect ITC claim: Interest + penalty up to 24% p.a. Risk-reward analysis suggests conservative approach."
        
        return "Financial analysis requires more data."


class VendorRiskAnalystAgent:
    """
    Specialist agent for vendor default risk prediction
    Uses ML to predict which vendors won't file on time
    """
    
    def __init__(self):
        self.risk_model = None
        self._model_loaded = False
    
    async def assess(self, invoice_data: Dict) -> Dict:
        """
        Assess vendor default risk
        Returns risk scores for each vendor
        """
        # Mock vendor risk assessment
        vendors = self._extract_vendors(invoice_data)
        
        high_risk_vendors = []
        for vendor in vendors[:5]:  # Top 5 vendors
            risk_score = 75  # Mock high risk
            high_risk_vendors.append({
                "vendor_name": vendor.get('vendor_name', 'Unknown'),
                "vendor_gstin": vendor.get('vendor_gstin', ''),
                "risk_score": risk_score,
                "risk_factors": [
                    "Late filing history (4/6 months)",
                    "GSTIN age < 2 years",
                    "High-risk industry sector"
                ],
                "probability_of_default": 0.65
            })
        
        return {
            "vendors_analyzed": len(vendors),
            "high_risk_count": len(high_risk_vendors),
            "high_risk_vendors": high_risk_vendors,
            "average_risk_score": 45,
            "recommendation": "send_reminders" if len(high_risk_vendors) > 2 else "monitor",
            "confidence": 0.78
        }
    
    def _extract_vendors(self, invoice_data: Dict) -> List[Dict]:
        """Extract unique vendors from invoice data"""
        # Mock implementation
        return [
            {"vendor_name": "Sharma Electronics", "vendor_gstin": "07AABCS1234A1Z5"},
            {"vendor_name": "Gupta Trading", "vendor_gstin": "27AABCG5678B1Z3"},
            {"vendor_name": "Delhi Components", "vendor_gstin": "07AABCD9012C1Z1"},
        ]
    
    async def opinion(self, topic: str, context: Dict) -> str:
        """Provide risk opinion for agent debates"""
        if topic == "vendor_default_risk":
            risk_data = context[3]
            high_risk_count = risk_data.get('high_risk_count', 0)
            
            if high_risk_count > 3:
                return f"⚠️ Risk Alert: {high_risk_count} vendors identified as high-risk for default. Recommend immediate WhatsApp/email reminders and consider provisional ITC claim."
            else:
                return f"✓ Risk Assessment: {high_risk_count} high-risk vendors. Standard follow-up procedures should suffice."
        
        return "Risk analysis requires vendor history data."


# Helper functions to get agent instances
def get_compliance_auditor_agent() -> ComplianceAuditorAgent:
    return ComplianceAuditorAgent()

def get_finance_optimizer_agent() -> FinanceOptimizerAgent:
    return FinanceOptimizerAgent()

def get_vendor_risk_analyst_agent() -> VendorRiskAnalystAgent:
    return VendorRiskAnalystAgent()
