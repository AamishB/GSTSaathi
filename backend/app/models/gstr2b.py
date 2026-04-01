"""
GSTR-2B Entry model for storing auto-drafted ITC data.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class GSTR2BEntry(Base):
    """GSTR-2B entry model storing auto-drafted ITC details from GST portal."""
    
    __tablename__ = "gstr2b_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    supplier_gstin = Column(String(15), nullable=False, index=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    taxable_value = Column(Float, nullable=False)
    igst = Column(Float, default=0.0)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    itc_eligible = Column(Boolean, default=True)
    itc_ineligible_reason = Column(String(255), nullable=True)
    import_batch_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to company
    company = relationship("Company", back_populates="gstr2b_entries")
    
    # Relationship to reconciliation results
    reconciliation = relationship("ReconciliationResult", back_populates="gstr2b_entry", uselist=False)
    
    def __repr__(self):
        return f"<GSTR2BEntry(id={self.id}, invoice_number={self.invoice_number}, taxable_value={self.taxable_value})>"
