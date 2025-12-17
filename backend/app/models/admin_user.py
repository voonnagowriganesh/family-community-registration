from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("super_admin", "verifier", "readonly", name="admin_role_enum"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
