from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class UserRejected(Base):
    __tablename__ = "users_rejected"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Original pending reference
    original_pending_id = Column(UUID(as_uuid=True), nullable=False)

    registration_id = Column(
    String(20),
    unique=True
    )

    # Identity
    mobile_number = Column(String(15), index=True)
    email = Column(String(255), index=True)

    # Personal details
    full_name = Column(String(150), nullable=False)
    surname = Column(String(80))
    desired_name = Column(String(150))
    father_or_husband_name = Column(String(150))
    mother_name = Column(String(150))
    date_of_birth = Column(String(20))
    gender = Column(String(20))
    blood_group = Column(String(10))

    marital_status = Column(String(30))

    # Community
    gothram = Column(String(120))
    aaradhya_daiva = Column(String(120))
    kula_devata = Column(String(120))

    # Current Address
    current_house_number = Column(String(60))
    current_village_city = Column(String(120))
    current_mandal = Column(String(120))
    current_district = Column(String(120))
    current_state = Column(String(120))
    current_country = Column(String(120))
    current_pin_code = Column(String(10))

    # Native Address
    native_house_number = Column(String(60))
    native_village_city = Column(String(120))
    native_mandal = Column(String(120))
    native_district = Column(String(120))
    native_state = Column(String(120))
    native_country = Column(String(120))
    native_pin_code = Column(String(10))

    # Education & work
    education = Column(String(120))
    occupation = Column(String(120))

    # Media
    photo_url = Column(Text)

    # Referral
    referred_by_name = Column(String(120))
    referred_mobile = Column(String(15))

    # Rejection info
    reject_reason = Column(Text, nullable=False)
    rejected_by_admin_id = Column(UUID(as_uuid=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Audit
    created_at = Column(DateTime(timezone=True))
