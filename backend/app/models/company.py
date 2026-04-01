"""
Company model for storing business profile.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Company(Base):
    """Company model storing GST registration and business details."""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    gstin = Column(String(15), unique=True, index=True, nullable=False)
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    address = Column(Text, nullable=False)
    state_code = Column(String(2), nullable=False)  # 2-digit state code
    turnover_slab = Column(String(20), nullable=False)  # below_1.5cr, 1.5cr_to_5cr, above_5cr
    filing_frequency = Column(String(20), default="monthly")  # monthly, quarterly
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="company")
    
    # Relationships to invoices and GSTR-2B entries
    invoices = relationship("Invoice", back_populates="company", cascade="all, delete-orphan")
    gstr2b_entries = relationship("GSTR2BEntry", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, gstin={self.gstin}, legal_name={self.legal_name})>"
