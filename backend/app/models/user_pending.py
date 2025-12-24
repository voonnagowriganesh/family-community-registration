from pydantic import BaseModel, model_validator
from sqlalchemy import Column, String, Boolean, Date, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base

class UserPending(Base):
    __tablename__ = "users_pending"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    registration_id = Column(
    String(20),
    unique=True,
    nullable=False,
    index=True
)


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

    marital_status = Column(
    Enum("Married", "Unmarried", "Prefer not to say", name="marital_status_enum"),
    nullable=False
    )

    gothram = Column(String(120), nullable=False)
    aaradhya_daiva = Column(String(120))
    kula_devata = Column(String(120))

    education = Column(String(120), nullable=False)
    occupation = Column(String(120), nullable=False)

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

    status = Column(Enum("pending", "hold", "rejected", name="user_status_enum"), default="pending")
    hold_reason = Column(Text)
    reject_reason = Column(Text)
    possible_duplicate = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())



    @model_validator(mode="after")
    def check_city_or_mandal(self):
        if not self.current_village_city and not self.current_mandal:
            raise ValueError(
                "Either current village/city or mandal is required"
            )
        return self

