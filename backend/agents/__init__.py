"""
GSTSaathi Agents Package
smolagents-based AI agents for GST compliance automation
"""

from .data_agent import ExcelDataExtractor, CSVDataExtractor, parse_invoice_data
from .mismatch_agent import GSTR2AComparator, analyze_mismatches
from .whatsapp_agent import MockWhatsAppSender, generate_vendor_reminders, send_mock_whatsapp

# Backward-compatible aliases for earlier class names.
DataAgent = ExcelDataExtractor
MismatchAgent = GSTR2AComparator
WhatsAppAgent = MockWhatsAppSender

__all__ = [
    'DataAgent',
    'ExcelDataExtractor',
    'CSVDataExtractor',
    'parse_invoice_data',
    'MismatchAgent',
    'GSTR2AComparator',
    'analyze_mismatches',
    'WhatsAppAgent',
    'MockWhatsAppSender',
    'generate_vendor_reminders',
    'send_mock_whatsapp',
]
