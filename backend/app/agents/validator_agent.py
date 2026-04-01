"""
ValidatorAgent for GSTIN and HSN validation.
Uses smolagents CodeAgent with custom validation tools.
"""
from typing import Dict, List, Any
import pandas as pd

from .base_agent import BaseAgent
from ..utils.gstin_validator import validate_gstin, is_valid_gstin
from ..utils.hsn_validator import validate_hsn_for_turnover, validate_hsn_format


def create_validator_agent() -> BaseAgent:
    """
    Create ValidatorAgent with all validation tools.
    
    Returns:
        Configured ValidatorAgent
    """
    from smolagents import tool
    
    agent = BaseAgent(
        name="ValidatorAgent",
        description="Validates GSTIN format, checksum, and HSN codes based on turnover slab",
    )
    
    @tool
    def validate_single_gstin(gstin: str) -> Dict:
        """
        Validate a single GSTIN.
        
        Args:
            gstin: GSTIN to validate
            
        Returns:
            Validation result dictionary
        """
        return validate_gstin(gstin)
    
    @tool
    def validate_gstin_list(gstins: List[str]) -> List[Dict]:
        """
        Validate a list of GSTINs.
        
        Args:
            gstins: List of GSTINs to validate
            
        Returns:
            List of validation results
        """
        results = []
        for gstin in gstins:
            result = validate_gstin(gstin)
            results.append({
                "gstin": gstin,
                "valid": result["valid"],
                "errors": result["errors"],
                "state_code": result.get("state_code"),
                "pan": result.get("pan"),
            })
        return results
    
    @tool
    def validate_hsn_code(hsn_code: str, turnover_slab: str = "1.5cr_to_5cr") -> Dict:
        """
        Validate HSN code based on turnover slab.
        
        Args:
            hsn_code: HSN code to validate
            turnover_slab: Turnover slab (below_1.5cr, 1.5cr_to_5cr, above_5cr)
            
        Returns:
            Validation result dictionary
        """
        return validate_hsn_for_turnover(hsn_code, turnover_slab)
    
    @tool
    def validate_dataframe_gstins(df: pd.DataFrame, column_name: str = "gstin") -> Dict:
        """
        Validate all GSTINs in a DataFrame column.
        
        Args:
            df: pandas DataFrame
            column_name: Name of the column containing GSTINs
            
        Returns:
            Dictionary with valid count, invalid count, and errors
        """
        if column_name not in df.columns:
            return {
                "success": False,
                "error": f"Column '{column_name}' not found in DataFrame",
            }
        
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for idx, gstin in df[column_name].items():
            if pd.isna(gstin) or gstin == "":
                continue
                
            result = validate_gstin(str(gstin))
            if result["valid"]:
                valid_count += 1
            else:
                invalid_count += 1
                errors.append({
                    "row": idx + 2,  # Excel row number
                    "gstin": gstin,
                    "errors": result["errors"],
                })
        
        return {
            "success": True,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "total": valid_count + invalid_count,
            "errors": errors[:100],  # Limit to first 100 errors
        }
    
    # Register tools
    agent.add_tool(validate_single_gstin)
    agent.add_tool(validate_gstin_list)
    agent.add_tool(validate_hsn_code)
    agent.add_tool(validate_dataframe_gstins)
    
    return agent


# Singleton instance
_validator_agent = None


def get_validator_agent() -> BaseAgent:
    """Get or create ValidatorAgent singleton."""
    global _validator_agent
    if _validator_agent is None:
        _validator_agent = create_validator_agent()
    return _validator_agent
