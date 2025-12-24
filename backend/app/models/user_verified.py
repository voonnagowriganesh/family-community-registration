from sqlalchemy import Column, String, Date, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class UserVerified(Base):
    __tablename__ = "users_verified"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id = Column(String(30), unique=True, nullable=False)

    registration_id = Column(String(20), unique=True, nullable=False, index=True)


    verification_type = Column(Enum("mobile", "email", name="verification_type_enum"), nullable=False)
    mobile_number = Column(String(10), unique=True)
    email = Column(String(150), unique=True)

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

    marital_status = Column(
    Enum("Married", "Unmarried", "Prefer not to say", name="marital_status_enum"),
    nullable=False
    )

    # Current Address
    current_house_number = Column(String(60))
    current_village_city = Column(String(120), nullable=True)
    current_mandal = Column(String(120), nullable=True)
    current_district = Column(String(120), nullable=False)
    current_state = Column(String(120), nullable=False)
    current_country = Column(String(120), default="India")
    current_pin_code = Column(String(10), nullable=False)

    #Native Address
    native_house_number = Column(String(60), nullable=False)
    native_village_city = Column(String(120), nullable=True)
    native_mandal = Column(String(120), nullable=True)
    native_district = Column(String(120), nullable=False)
    native_state = Column(String(120), nullable=False)
    native_country = Column(String(120), default="India")
    native_pin_code = Column(String(10),nullable=False)

    photo_url = Column(Text, nullable=False)
    pdf_url = Column(Text, nullable=False)

    referred_by_name = Column(String(150), nullable=False)
    referred_mobile = Column(String(10), nullable=False)
    feedback = Column(Text)

    approved_at = Column(DateTime, server_default=func.now())
    # ✅ ADD THESE TWO (MISSING)
    approved_by = Column(UUID(as_uuid=True), nullable=True)


    
    
