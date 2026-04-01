"""
Reconciliation Result model for storing invoice matching results.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class ReconciliationResult(Base):
    """Reconciliation result model storing invoice vs GSTR-2B matching results."""
    
    __tablename__ = "reconciliation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), index=True, nullable=False)
    gstr2b_entry_id = Column(Integer, ForeignKey("gstr2b_entries.id"), index=True, nullable=True)
    match_status = Column(String(30), nullable=False)  # matched, missing_in_gstr2b, value_mismatch, gstin_error, timing_diff
    match_confidence = Column(String(20), default="exact")  # exact, partial, no_match
    taxable_value_diff = Column(Float, nullable=True)
    tax_value_diff = Column(Float, nullable=True)
    mismatch_category = Column(String(50), nullable=True)
    action_taken = Column(String(20), default="pending")  # pending, resolved, reversed
    reconciled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="reconciliation")
    gstr2b_entry = relationship("GSTR2BEntry", back_populates="reconciliation")
    
    def __repr__(self):
        return f"<ReconciliationResult(id={self.id}, match_status={self.match_status})>"
