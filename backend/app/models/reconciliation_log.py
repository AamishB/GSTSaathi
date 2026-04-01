"""
Reconciliation log model for tracking reconciliation runs (F42).
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from ..database import Base


class ReconciliationLog(Base):
    """Stores one record per reconciliation run."""

    __tablename__ = "reconciliation_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    job_id = Column(String(64), index=True, nullable=False)
    matched_count = Column(Integer, default=0)
    mismatch_count = Column(Integer, default=0)
    itc_at_risk = Column(Float, default=0.0)
    status = Column(String(20), default="completed")  # completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ReconciliationLog(id={self.id}, job_id={self.job_id}, status={self.status})>"
