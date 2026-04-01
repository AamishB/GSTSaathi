"""
Invoice model for storing uploaded invoice data.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Invoice(Base):
    """Invoice model storing outward/inward supply invoice details."""
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    supplier_gstin = Column(String(15), nullable=False, index=True)
    supplier_name = Column(String(255), nullable=False)
    recipient_gstin = Column(String(15), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=False)
    taxable_value = Column(Float, nullable=False)
    igst = Column(Float, default=0.0)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    total_value = Column(Float, nullable=False)
    hsn_code = Column(String(8), nullable=True)
    place_of_supply = Column(String(2), nullable=False)  # State code
    is_duplicate = Column(Boolean, default=False)
    upload_batch_id = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to company
    company = relationship("Company", back_populates="invoices")
    
    # Relationship to reconciliation results
    reconciliation = relationship("ReconciliationResult", back_populates="invoice", uselist=False)
    
    # Composite index for duplicate detection
    __table_args__ = (
        Index('idx_unique_invoice', 'company_id', 'invoice_number', 'invoice_date'),
    )
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, total_value={self.total_value})>"
