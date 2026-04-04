"""
AI Agents for GSTSaathi application.
All P0 agents using smolagents CodeAgent architecture.
"""
from .base_agent import BaseAgent
from .validator_agent import create_validator_agent, get_validator_agent
from .data_agent import create_data_agent, get_data_agent
from .reconciliation_agent import create_reconciliation_agent, get_reconciliation_agent
from .compliance_agent import create_compliance_agent, get_compliance_agent
from .filing_agent import create_filing_agent, get_filing_agent
from .orchestrator import create_orchestrator_agent, get_orchestrator_agent
from .whatsapp_agent import generate_vendor_reminders, send_mock_whatsapp

__all__ = [
    # Base
    "BaseAgent",
    # Agent factories
    "create_validator_agent",
    "create_data_agent",
    "create_reconciliation_agent",
    "create_compliance_agent",
    "create_filing_agent",
    "create_orchestrator_agent",
    # Singleton getters
    "get_validator_agent",
    "get_data_agent",
    "get_reconciliation_agent",
    "get_compliance_agent",
    "get_filing_agent",
    "get_orchestrator_agent",
    # WhatsApp helpers
    "generate_vendor_reminders",
    "send_mock_whatsapp",
]
