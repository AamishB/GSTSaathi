"""
Supervisor Agent - Multi-Agent Orchestrator
Coordinates specialist agents, assigns tasks, and manages consensus
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class AgentRole(str, Enum):
    SUPERVISOR = "supervisor"
    GST_EXPERT = "gst_expert"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    FINANCE_OPTIMIZER = "finance_optimizer"
    VENDOR_RISK_ANALYST = "vendor_risk_analyst"


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    SPEAKING = "speaking"
    WAITING = "waiting"
    COMPLETED = "completed"


class AgentMessage:
    """Represents a message from an agent in the debate"""
    
    def __init__(self, agent_role: AgentRole, content: str, 
                 timestamp: str = None, metadata: Dict = None):
        self.agent_role = agent_role
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "agent_role": self.agent_role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class SupervisorAgent:
    """
    Orchestrates multi-agent collaboration
    - Assigns tasks to specialist agents
    - Manages agent debates
    - Reaches consensus through voting
    - Provides final recommendations
    """
    
    def __init__(self):
        self.agents: Dict[AgentRole, Any] = {}
        self.message_history: List[AgentMessage] = []
        self.current_task: Optional[str] = None
        self.consensus_reached: bool = False
        self.final_recommendation: Optional[Dict] = None
        
        # Agent status tracking
        self.agent_status: Dict[AgentRole, AgentStatus] = {
            role: AgentStatus.IDLE for role in AgentRole
        }
        
        # Initialize specialist agents (lazy loading)
        self._gst_expert = None
        self._compliance_auditor = None
        self._finance_optimizer = None
        self._vendor_risk_analyst = None
    
    def register_agent(self, role: AgentRole, agent: Any):
        """Register a specialist agent"""
        self.agents[role] = agent
    
    async def initialize_specialists(self):
        """Initialize all specialist agents"""
        from agents.gst_expert_agent import GSTExpertAgent
        from agents.compliance_agent import ComplianceAuditorAgent
        from agents.finance_agent import FinanceOptimizerAgent
        from agents.vendor_risk_agent import VendorRiskAnalystAgent
        
        self._gst_expert = GSTExpertAgent()
        self._compliance_auditor = ComplianceAuditorAgent()
        self._finance_optimizer = FinanceOptimizerAgent()
        self._vendor_risk_analyst = VendorRiskAnalystAgent()
        
        self.register_agent(AgentRole.GST_EXPERT, self._gst_expert)
        self.register_agent(AgentRole.COMPLIANCE_AUDITOR, self._compliance_auditor)
        self.register_agent(AgentRole.FINANCE_OPTIMIZER, self._finance_optimizer)
        self.register_agent(AgentRole.VENDOR_RISK_ANALYST, self._vendor_risk_analyst)
    
    def update_agent_status(self, role: AgentRole, status: AgentStatus):
        """Update agent status for visualization"""
        self.agent_status[role] = status
    
    def add_message(self, role: AgentRole, content: str, metadata: Dict = None):
        """Add agent message to debate history"""
        message = AgentMessage(role, content, metadata=metadata)
        self.message_history.append(message)
        return message
    
    async def analyze_invoice(self, invoice_data: Dict, gstr2a_data: List) -> Dict:
        """
        Coordinate multi-agent analysis of invoice data
        Returns comprehensive analysis with agent recommendations
        """
        self.current_task = "invoice_analysis"
        self.message_history = []
        self.consensus_reached = False
        
        results = {}
        
        # Phase 1: Parallel Analysis
        self.update_agent_status(AgentRole.GST_EXPERT, AgentStatus.THINKING)
        self.update_agent_status(AgentRole.COMPLIANCE_AUDITOR, AgentStatus.THINKING)
        self.update_agent_status(AgentRole.FINANCE_OPTIMIZER, AgentStatus.THINKING)
        self.update_agent_status(AgentRole.VENDOR_RISK_ANALYST, AgentStatus.THINKING)
        
        # Run specialist analyses
        gst_analysis = await self._gst_expert.analyze(invoice_data, gstr2a_data)
        self.add_message(AgentRole.GST_EXPERT, 
                        f"Analyzed {len(invoice_data)} invoices. {gst_analysis['compliant_count']} compliant with GST laws.",
                        {"analysis": gst_analysis})
        self.update_agent_status(AgentRole.GST_EXPERT, AgentStatus.COMPLETED)
        
        compliance_check = await self._compliance_auditor.audit(invoice_data, gstr2a_data)
        self.add_message(AgentRole.COMPLIANCE_AUDITOR,
                        f"Found {compliance_check['risk_count']} high-risk invoices. Overall risk score: {compliance_check['overall_risk_score']}/100",
                        {"audit": compliance_check})
        self.update_agent_status(AgentRole.COMPLIANCE_AUDITOR, AgentStatus.COMPLETED)
        
        finance_analysis = await self._finance_optimizer.optimize(invoice_data)
        self.add_message(AgentRole.FINANCE_OPTIMIZER,
                        f"Optimal filing date: {finance_analysis['optimal_date']}. Potential savings: ₹{finance_analysis['savings']}",
                        {"finance": finance_analysis})
        self.update_agent_status(AgentRole.FINANCE_OPTIMIZER, AgentStatus.COMPLETED)
        
        risk_assessment = await self._vendor_risk_analyst.assess(invoice_data)
        self.add_message(AgentRole.VENDOR_RISK_ANALYST,
                        f"Assessed {risk_assessment['vendors_analyzed']} vendors. {risk_assessment['high_risk_count']} high-risk vendors identified.",
                        {"risk": risk_assessment})
        self.update_agent_status(AgentRole.VENDOR_RISK_ANALYST, AgentStatus.COMPLETED)
        
        # Phase 2: Agent Debate
        await self._run_debate(gst_analysis, compliance_check, finance_analysis, risk_assessment)
        
        # Phase 3: Consensus & Recommendation
        self.final_recommendation = await self._generate_recommendation(
            gst_analysis, compliance_check, finance_analysis, risk_assessment
        )
        
        return {
            "gst_analysis": gst_analysis,
            "compliance_check": compliance_check,
            "finance_analysis": finance_analysis,
            "risk_assessment": risk_assessment,
            "debate_history": [m.to_dict() for m in self.message_history],
            "recommendation": self.final_recommendation,
            "consensus_reached": self.consensus_reached
        }
    
    async def _run_debate(self, gst_analysis: Dict, compliance_check: Dict, 
                         finance_analysis: Dict, risk_assessment: Dict):
        """Facilitate agent debate on edge cases"""
        
        # Identify edge cases for debate
        edge_cases = []
        
        if compliance_check['overall_risk_score'] > 50:
            edge_cases.append("high_risk_invoices")
        
        if finance_analysis['savings'] > 10000:
            edge_cases.append("cash_flow_optimization")
        
        if risk_assessment['high_risk_count'] > 3:
            edge_cases.append("vendor_default_risk")
        
        if not edge_cases:
            self.consensus_reached = True
            return
        
        # Run debate for each edge case
        for edge_case in edge_cases:
            await self._debate_edge_case(edge_case, gst_analysis, compliance_check, 
                                        finance_analysis, risk_assessment)
    
    async def _debate_edge_case(self, edge_case: str, *analyses):
        """Run structured debate on specific edge case"""
        
        self.update_agent_status(AgentRole.GST_EXPERT, AgentStatus.SPEAKING)
        self.update_agent_status(AgentRole.COMPLIANCE_AUDITOR, AgentStatus.SPEAKING)
        self.update_agent_status(AgentRole.FINANCE_OPTIMIZER, AgentStatus.SPEAKING)
        
        if edge_case == "high_risk_invoices":
            # GST Expert opinion
            gst_opinion = await self._gst_expert.opinion("high_risk_invoices", analyses)
            self.add_message(AgentRole.GST_EXPERT, gst_opinion, {"debate": edge_case})
            
            # Compliance Auditor counter-opinion
            compliance_opinion = await self._compliance_auditor.opinion("high_risk_invoices", analyses)
            self.add_message(AgentRole.COMPLIANCE_AUDITOR, compliance_opinion, {"debate": edge_case})
            
            # Finance Optimizer input
            finance_opinion = await self._finance_optimizer.opinion("high_risk_invoices", analyses)
            self.add_message(AgentRole.FINANCE_OPTIMIZER, finance_opinion, {"debate": edge_case})
        
        elif edge_case == "cash_flow_optimization":
            # Debate on filing timing
            gst_timing = await self._gst_expert.opinion("filing_timing", analyses)
            self.add_message(AgentRole.GST_EXPERT, gst_timing, {"debate": edge_case})
            
            finance_timing = await self._finance_optimizer.opinion("filing_timing", analyses)
            self.add_message(AgentRole.FINANCE_OPTIMIZER, finance_timing, {"debate": edge_case})
        
        elif edge_case == "vendor_default_risk":
            # Debate on vendor risk mitigation
            risk_opinion = await self._vendor_risk_analyst.opinion("vendor_default_risk", analyses)
            self.add_message(AgentRole.VENDOR_RISK_ANALYST, risk_opinion, {"debate": edge_case})
            
            compliance_mitigation = await self._compliance_auditor.opinion("vendor_default_risk", analyses)
            self.add_message(AgentRole.COMPLIANCE_AUDITOR, compliance_mitigation, {"debate": edge_case})
        
        self.update_agent_status(AgentRole.GST_EXPERT, AgentStatus.IDLE)
        self.update_agent_status(AgentRole.COMPLIANCE_AUDITOR, AgentStatus.IDLE)
        self.update_agent_status(AgentRole.FINANCE_OPTIMIZER, AgentStatus.IDLE)
        self.update_agent_status(AgentRole.VENDOR_RISK_ANALYST, AgentStatus.IDLE)
    
    async def _generate_recommendation(self, gst_analysis: Dict, compliance_check: Dict,
                                       finance_analysis: Dict, risk_assessment: Dict) -> Dict:
        """Generate final consensus recommendation"""
        
        # Calculate weighted scores
        compliance_score = 100 - compliance_check['overall_risk_score']
        finance_score = min(100, (finance_analysis['savings'] / 1000) * 10)
        risk_score = 100 - (risk_assessment['high_risk_count'] * 10)
        
        # Determine action
        if compliance_score > 80 and risk_score > 70:
            action = "file_immediately"
            confidence = 0.9
            reasoning = "High compliance, low risk - proceed with filing"
        elif compliance_score > 60 and finance_analysis['savings'] > 5000:
            action = "delay_filing"
            confidence = 0.75
            reasoning = f"Delay to {finance_analysis['optimal_date']} for ₹{finance_analysis['savings']} savings"
        else:
            action = "review_required"
            confidence = 0.6
            reasoning = "Manual review recommended due to compliance concerns"
        
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "optimal_filing_date": finance_analysis.get('optimal_date'),
            "expected_savings": finance_analysis.get('savings', 0),
            "risk_factors": risk_assessment.get('high_risk_vendors', []),
            "compliance_issues": compliance_check.get('issues', []),
            "agent_votes": {
                "gst_expert": "approve" if compliance_score > 70 else "reject",
                "compliance_auditor": "approve" if compliance_score > 80 else "review",
                "finance_optimizer": "optimize" if finance_analysis['savings'] > 5000 else "approve",
                "vendor_risk_analyst": "approve" if risk_score > 70 else "caution"
            }
        }
    
    def get_agent_status(self) -> Dict:
        """Get current status of all agents for visualization"""
        return {
            role.value: status.value 
            for role, status in self.agent_status.items()
        }
    
    def get_debate_history(self) -> List[Dict]:
        """Get full debate history for display"""
        return [m.to_dict() for m in self.message_history]


# Singleton instance
_supervisor_instance: Optional[SupervisorAgent] = None

def get_supervisor_agent() -> SupervisorAgent:
    """Get or create supervisor agent singleton"""
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = SupervisorAgent()
    return _supervisor_instance
