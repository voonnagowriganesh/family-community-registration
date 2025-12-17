from sqlalchemy import Column, String, Boolean, Date, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class UserPending(Base):
    __tablename__ = "users_pending"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    verification_type = Column(Enum("mobile", "email", name="verification_type_enum"), nullable=False)
    mobile_number = Column(String(10), unique=True)
    email = Column(String(150), unique=True)
    is_verified = Column(Boolean, default=False)

    full_name = Column(String(150), nullable=False)
    surname = Column(String(80), nullable=False)
    desired_name = Column(String(150), nullable=False)
    father_or_husband_name = Column(String(150), nullable=False)
    mother_name = Column(String(150), nullable=False)
    date_of_birth = Column(Date)

    gender = Column(String(20))
    blood_group = Column(String(5))

    gothram = Column(String(120), nullable=False)
    aaradhya_daiva = Column(String(120))
    kula_devata = Column(String(120))

    education = Column(String(120), nullable=False)
    occupation = Column(String(120), nullable=False)

    house_number = Column(String(60))
    village_city = Column(String(120), nullable=False)
    mandal = Column(String(120), nullable=False)
    district = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    country = Column(String(120), default="India")
    pin_code = Column(String(10), nullable=False)

    photo_url = Column(Text, nullable=False)
    pdf_url = Column(Text, nullable=False)

    referred_by_name = Column(String(150), nullable=False)
    referred_mobile = Column(String(10), nullable=False)
    feedback = Column(Text)

    status = Column(Enum("pending", "hold", "rejected", name="user_status_enum"), default="pending")
    hold_reason = Column(Text)
    reject_reason = Column(Text)
    possible_duplicate = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
