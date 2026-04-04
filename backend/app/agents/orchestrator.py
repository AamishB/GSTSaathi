"""
OrchestratorAgent for coordinating agent workflows.
Basic agent coordination for P0 (LangGraph in Phase 2).
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import pandas as pd

from .base_agent import BaseAgent
from .validator_agent import get_validator_agent
from .data_agent import get_data_agent
from .reconciliation_agent import get_reconciliation_agent
from .compliance_agent import get_compliance_agent
from .filing_agent import get_filing_agent


def create_orchestrator_agent() -> BaseAgent:
    """
    Create OrchestratorAgent that coordinates all other agents.
    
    Returns:
        Configured OrchestratorAgent
    """
    from smolagents import tool
    
    # Initialize sub-agents
    validator_agent = get_validator_agent()
    data_agent = get_data_agent()
    reconciliation_agent = get_reconciliation_agent()
    compliance_agent = get_compliance_agent()
    filing_agent = get_filing_agent()
    
    agent = BaseAgent(
        name="OrchestratorAgent",
        description="Coordinates workflows between ValidatorAgent, DataAgent, ReconciliationAgent, ComplianceAgent, and FilingAgent",
    )
    
    @tool
    def process_invoice_upload(file_path: str, company_id: int, turnover_slab: str) -> Dict:
        """
        Process uploaded invoice file through validation and parsing.
        
        Workflow:
        1. Parse file (DataAgent)
        2. Validate GSTINs (ValidatorAgent)
        3. Check duplicates (DataAgent)
        4. Transform to schema (DataAgent)
        
        Args:
            file_path: Path to uploaded file
            company_id: Company ID
            turnover_slab: Turnover slab for HSN validation
            
        Returns:
            Processing results
        """
        results = {
            "workflow": "invoice_upload",
            "file_path": file_path,
            "company_id": company_id,
            "started_at": datetime.now().isoformat(),
            "steps": [],
        }
        
        # Step 1: Parse file
        parse_result = data_agent.execute(
            "Parse invoice file",
            {"file_path": file_path, "action": "parse"}
        )
        results["steps"].append({
            "step": 1,
            "name": "Parse File",
            "agent": "DataAgent",
            "result": parse_result,
        })
        
        if not parse_result.get("success"):
            results["status"] = "failed"
            results["error"] = "Failed to parse file"
            return results
        
        # Step 2: Validate GSTINs
        if "sample_data" in parse_result:
            df = pd.DataFrame(parse_result["sample_data"])
            if 'supplier_gstin' in df.columns:
                validation_result = validator_agent.execute(
                    "Validate GSTINs in dataframe",
                    {"dataframe": df, "column": "supplier_gstin"}
                )
                results["steps"].append({
                    "step": 2,
                    "name": "Validate GSTINs",
                    "agent": "ValidatorAgent",
                    "result": validation_result,
                })
        
        # Step 3: Check duplicates
        duplicate_result = data_agent.execute(
            "Check duplicates",
            {"file_path": file_path, "action": "duplicates"}
        )
        results["steps"].append({
            "step": 3,
            "name": "Check Duplicates",
            "agent": "DataAgent",
            "result": duplicate_result,
        })
        
        # Step 4: Validate invoice data
        validation_result = data_agent.execute(
            "Validate invoice data",
            {"file_path": file_path, "action": "validate"}
        )
        results["steps"].append({
            "step": 4,
            "name": "Validate Invoice Data",
            "agent": "DataAgent",
            "result": validation_result,
        })
        
        results["status"] = "completed"
        results["completed_at"] = datetime.now().isoformat()
        
        return results
    
    @tool
    def run_reconciliation(invoices_df: pd.DataFrame, gstr2b_df: pd.DataFrame) -> Dict:
        """
        Run invoice reconciliation with GSTR-2B.
        
        Workflow:
        1. Match invoices (ReconciliationAgent)
        2. Classify mismatches (ReconciliationAgent)
        3. Calculate statistics
        
        Args:
            invoices_df: DataFrame with invoice data
            gstr2b_df: DataFrame with GSTR-2B data
            
        Returns:
            Reconciliation results
        """
        results = {
            "workflow": "reconciliation",
            "started_at": datetime.now().isoformat(),
        }
        
        # Run matching
        match_result = reconciliation_agent.execute(
            "Match invoices with GSTR-2B",
            {"invoices_df": invoices_df, "gstr2b_df": gstr2b_df}
        )
        
        if not match_result.get("success"):
            results["status"] = "failed"
            results["error"] = "Failed to reconcile invoices"
            return results
        
        results["match_result"] = match_result
        results["statistics"] = match_result.get("statistics", {})
        results["status"] = "completed"
        results["completed_at"] = datetime.now().isoformat()
        
        return results
    
    @tool
    def calculate_compliance_metrics(invoices: List[Dict], gstr2b_entries: List[Dict], reconciliation_results: List[Dict]) -> Dict:
        """
        Calculate compliance metrics and dashboard data.
        
        Args:
            invoices: List of invoices
            gstr2b_entries: List of GSTR-2B entries
            reconciliation_results: List of reconciliation results
            
        Returns:
            Dashboard metrics
        """
        # Calculate eligible ITC from matched invoices
        matched = [r for r in reconciliation_results if isinstance(r, dict) and r.get('match_status') == 'matched']
        
        itc_result = compliance_agent.execute(
            "Calculate eligible ITC",
            {"matched_invoices": matched}
        )
        
        # Calculate ITC at risk
        missing = [r for r in reconciliation_results if isinstance(r, dict) and r.get('match_status') == 'missing_in_gstr2b']
        
        itc_at_risk_result = compliance_agent.execute(
            "Calculate ITC at risk",
            {"missing_invoices": missing}
        )
        
        # Calculate total sales and output GST
        total_sales = sum(float(inv.get('total_value', 0)) for inv in invoices)
        output_igst = sum(float(inv.get('igst', 0)) for inv in invoices)
        output_cgst = sum(float(inv.get('cgst', 0)) for inv in invoices)
        output_sgst = sum(float(inv.get('sgst', 0)) for inv in invoices)
        
        # Calculate net GST payable
        net_gst_result = compliance_agent.execute(
            "Calculate net GST liability",
            {
                "output_gst": {
                    "igst": output_igst,
                    "cgst": output_cgst,
                    "sgst": output_sgst,
                },
                "eligible_itc": itc_result.get("breakdown", {}),
            }
        )
        
        return {
            "total_sales": round(total_sales, 2),
            "total_purchases": sum(float(e.get('taxable_value', 0)) for e in gstr2b_entries),
            "output_gst": round(output_igst + output_cgst + output_sgst, 2),
            "itc_available": itc_result.get("eligible_itc", 0),
            "net_gst_payable": net_gst_result.get("net_gst_payable", 0),
            "itc_at_risk": itc_at_risk_result.get("total_itc_at_risk", 0),
            "reconciliation_summary": {
                "total_invoices": len(invoices),
                "matched_count": len(matched),
                "missing_count": len(missing),
            },
        }
    
    @tool
    def generate_exports(invoices: List[Dict], company_gstin: str, output_gst: Dict, eligible_itc: Dict, period: str) -> Dict:
        """
        Generate export files (GSTR-1, GSTR-3B, reports).
        
        Args:
            invoices: List of invoices
            company_gstin: Company GSTIN
            output_gst: Output GST liability
            eligible_itc: Eligible ITC
            period: Period in MM-YYYY format
            
        Returns:
            Export generation results
        """
        results = {
            "workflow": "export_generation",
            "started_at": datetime.now().isoformat(),
            "exports": [],
        }
        
        # Generate GSTR-1
        gstr1_result = filing_agent.execute(
            "Generate GSTR-1",
            {
                "invoices": invoices,
                "company_gstin": company_gstin,
                "period": period,
            }
        )
        results["exports"].append({
            "type": "GSTR-1",
            "result": gstr1_result,
        })
        
        # Generate GSTR-3B
        gstr3b_result = filing_agent.execute(
            "Generate GSTR-3B",
            {
                "output_gst": output_gst,
                "eligible_itc": eligible_itc,
                "period": period,
            }
        )
        results["exports"].append({
            "type": "GSTR-3B",
            "result": gstr3b_result,
        })
        
        # Generate B2B report
        b2b_result = filing_agent.execute(
            "Generate B2B report",
            {"invoices": invoices}
        )
        results["exports"].append({
            "type": "B2B Report",
            "result": b2b_result,
        })
        
        results["status"] = "completed"
        results["completed_at"] = datetime.now().isoformat()
        
        return results
    
    # Register tools
    agent.add_tool(process_invoice_upload)
    agent.add_tool(run_reconciliation)
    agent.add_tool(calculate_compliance_metrics)
    agent.add_tool(generate_exports)

    def execute(task: str, context: Dict = None) -> Dict:
        """
        Execute orchestrator workflows deterministically for known tasks.
        """
        context = context or {}
        task_lower = task.lower() if task else ""

        if "upload" in task_lower or context.get("workflow") == "invoice_upload":
            return process_invoice_upload(
                context.get("file_path", ""),
                int(context.get("company_id", 0) or 0),
                context.get("turnover_slab", "1.5cr_to_5cr"),
            )

        if "reconciliation" in task_lower or context.get("workflow") == "reconciliation":
            invoices_df = context.get("invoices_df")
            gstr2b_df = context.get("gstr2b_df")
            if invoices_df is None or gstr2b_df is None:
                return {
                    "success": False,
                    "error": "invoices_df and gstr2b_df are required",
                }
            return run_reconciliation(invoices_df, gstr2b_df)

        if "compliance" in task_lower or context.get("workflow") == "compliance_metrics":
            return calculate_compliance_metrics(
                context.get("invoices", []),
                context.get("gstr2b_entries", []),
                context.get("reconciliation_results", []),
            )

        if "export" in task_lower or context.get("workflow") == "export_generation":
            return generate_exports(
                context.get("invoices", []),
                context.get("company_gstin", ""),
                context.get("output_gst", {}),
                context.get("eligible_itc", {}),
                context.get("period", ""),
            )

        return {
            "success": False,
            "error": f"Unsupported orchestrator task: {task}",
        }

    agent.execute = execute
    
    return agent


# Singleton instance
_orchestrator_agent = None


def get_orchestrator_agent() -> BaseAgent:
    """Get or create OrchestratorAgent singleton."""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        _orchestrator_agent = create_orchestrator_agent()
    return _orchestrator_agent
