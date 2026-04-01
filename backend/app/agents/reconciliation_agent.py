"""
ReconciliationAgent for matching invoices with GSTR-2B data.
Uses smolagents CodeAgent with pandas-based matching tools.
"""
from typing import Dict, List, Any
import pandas as pd

from .base_agent import BaseAgent


def create_reconciliation_agent() -> BaseAgent:
    """
    Create ReconciliationAgent with all matching tools.
    
    Returns:
        Configured ReconciliationAgent
    """
    from smolagents import tool
    
    agent = BaseAgent(
        name="ReconciliationAgent",
        description="Matches invoices with GSTR-2B, classifies mismatches, calculates statistics",
    )
    
    @tool
    def exact_match_invoices(invoices_df: pd.DataFrame, gstr2b_df: pd.DataFrame) -> Dict:
        """
        Match invoices with GSTR-2B using exact matching.
        
        Match criteria:
        - Supplier GSTIN (exact)
        - Invoice Number (exact)
        - Invoice Date (exact)
        - Taxable Value (exact)
        
        Args:
            invoices_df: DataFrame with invoice data
            gstr2b_df: DataFrame with GSTR-2B data
            
        Returns:
            Dictionary with match results and statistics
        """
        # Prepare DataFrames for merging
        inv_df = invoices_df.copy()
        gstr_df = gstr2b_df.copy()
        
        # Normalize date columns
        for df in [inv_df, gstr_df]:
            if 'invoice_date' in df.columns:
                df['invoice_date'] = pd.to_datetime(df['invoice_date']).dt.date
        
        # Perform left join to find unmatched invoices
        merged = pd.merge(
            inv_df,
            gstr_df,
            on=['supplier_gstin', 'invoice_number', 'invoice_date'],
            how='left',
            indicator=True,
            suffixes=('_inv', '_gstr2b')
        )
        
        # Classify matches
        def classify_match(row):
            if row['_merge'] == 'both':
                # Check taxable value match
                inv_val = row.get('taxable_value_inv', row.get('taxable_value'))
                gstr_val = row.get('taxable_value_gstr2b', row.get('taxable_value'))
                
                if pd.isna(gstr_val):
                    return 'matched'
                
                if abs(float(inv_val) - float(gstr_val)) < 1:  # ₹1 tolerance
                    return 'matched'
                else:
                    return 'value_mismatch'
            else:
                return 'missing_in_gstr2b'
        
        merged['match_status'] = merged.apply(classify_match, axis=1)
        
        # Calculate statistics
        total_invoices = len(merged)
        matched = merged[merged['match_status'] == 'matched']
        missing = merged[merged['match_status'] == 'missing_in_gstr2b']
        value_mismatch = merged[merged['match_status'] == 'value_mismatch']
        
        # Calculate values
        total_value = merged.get('taxable_value_inv', merged.get('taxable_value', pd.Series([0]))).sum()
        matched_value = matched.get('taxable_value_inv', matched.get('taxable_value', pd.Series([0]))).sum()
        missing_value = missing.get('taxable_value_inv', missing.get('taxable_value', pd.Series([0]))).sum()
        
        return {
            "success": True,
            "total_invoices": total_invoices,
            "matched_count": len(matched),
            "missing_count": len(missing),
            "value_mismatch_count": len(value_mismatch),
            "match_percentage": round(len(matched) / total_invoices * 100, 2) if total_invoices > 0 else 0,
            "total_taxable_value": round(total_value, 2),
            "matched_taxable_value": round(matched_value, 2),
            "missing_taxable_value": round(missing_value, 2),
            "itc_at_risk": round(missing_value * 0.18, 2),
            "matches": merged.to_dict('records'),
        }
    
    @tool
    def classify_mismatch(match_status: str) -> Dict:
        """
        Classify the type of mismatch for an invoice.
        
        Categories:
        - missing_in_gstr2b: Invoice booked but not in GSTR-2B
        - value_mismatch: Taxable value differs
        - gstin_error: Wrong GSTIN in invoice or GSTR-2B
        - timing_diff: Invoice date vs filing period mismatch
        
        Args:
            match_status: Match status from reconciliation
            
        Returns:
            Classified mismatch with recommended action
        """
        classification = {
            "match_status": match_status,
            "mismatch_category": None,
            "description": None,
            "recommended_action": None,
        }
        
        if match_status == 'matched':
            classification["mismatch_category"] = "none"
            classification["description"] = "Invoice matched successfully"
            classification["recommended_action"] = "No action needed"
            
        elif match_status == 'missing_in_gstr2b':
            classification["mismatch_category"] = "missing_in_gstr2b"
            classification["description"] = "Invoice booked in books but supplier has not filed in GSTR-1"
            classification["recommended_action"] = "Contact supplier to file GSTR-1"
            
        elif match_status == 'value_mismatch':
            classification["mismatch_category"] = "value_mismatch"
            classification["description"] = "Taxable value in books differs from GSTR-2B"
            classification["recommended_action"] = "Verify invoice with supplier, may need amendment"
            
        elif match_status == 'gstin_error':
            classification["mismatch_category"] = "gstin_error"
            classification["description"] = "GSTIN mismatch between invoice and GSTR-2B"
            classification["recommended_action"] = "Verify correct GSTIN with supplier"
            
        elif match_status == 'timing_diff':
            classification["mismatch_category"] = "timing_diff"
            classification["description"] = "Invoice date differs from GSTR-2B filing period"
            classification["recommended_action"] = "Check if invoice belongs to correct period"
        
        return classification
    
    # Register tools
    agent.add_tool(exact_match_invoices)
    agent.add_tool(classify_mismatch)

    def execute(task: str, context: Dict = None) -> Dict:
        """
        Execute reconciliation deterministically without relying on LLM generation.
        """
        if context is None:
            return {
                "success": False,
                "error": "Missing reconciliation context",
            }

        invoices_df = context.get("invoices_df")
        gstr2b_df = context.get("gstr2b_df")

        if invoices_df is None or gstr2b_df is None:
            return {
                "success": False,
                "error": "Both invoices_df and gstr2b_df are required",
            }

        if not isinstance(invoices_df, pd.DataFrame):
            invoices_df = pd.DataFrame(invoices_df)
        if not isinstance(gstr2b_df, pd.DataFrame):
            gstr2b_df = pd.DataFrame(gstr2b_df)

        return exact_match_invoices(invoices_df, gstr2b_df)

    agent.execute = execute
    
    return agent


# Singleton instance
_reconciliation_agent = None


def get_reconciliation_agent() -> BaseAgent:
    """Get or create ReconciliationAgent singleton."""
    global _reconciliation_agent
    if _reconciliation_agent is None:
        _reconciliation_agent = create_reconciliation_agent()
    return _reconciliation_agent
