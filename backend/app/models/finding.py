from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    
    title = Column(String, nullable=False)           # e.g., "Open Port 21 (FTP)"
    severity = Column(String, nullable=False)        # Critical, High, Medium, Low, Info
    description = Column(Text, nullable=True)        # Technical details
    remediation = Column(Text, nullable=True)        # How to fix it
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    scan = relationship("Scan", back_populates="findings")
    target = relationship("Target", back_populates="findings")