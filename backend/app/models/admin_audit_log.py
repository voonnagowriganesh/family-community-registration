import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.models.base import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # APPROVE / REJECT / HOLD
    target_type = Column(String, nullable=False)  # user
    target_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
