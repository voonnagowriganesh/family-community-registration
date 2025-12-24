from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from enum import Enum

class VerificationType(str, Enum):
    mobile = "mobile"
    email = "email"


class UserRegistrationRequest(BaseModel):
    verification_type: VerificationType
    mobile_number: Optional[str]
    email: Optional[EmailStr] 

    full_name: str
    surname: str  # Mothers Maiden Name as Surname
    desired_name: str
    father_or_husband_name: str
    mother_name: str
    date_of_birth: Optional[date]

    gender: Optional[str]
    marital_status: Optional[str] = "Prefer not to say"
    blood_group: Optional[str]

    gothram: str
    aaradhya_daiva: Optional[str]
    kula_devata: Optional[str]

    education: str
    occupation: str

    current_house_number: Optional[str]
    current_village_city: Optional[str]
    current_mandal: Optional[str]
    current_district: str
    current_state: str
    current_country: Optional[str] = "India"
    current_pin_code: str

    native_house_number: Optional[str]
    native_village_city: Optional[str]
    native_mandal: Optional[str]
    native_district: str
    native_state: str
    native_country: Optional[str] = "India"
    native_pin_code: str


    photo_url: str

    referred_by_name: str
    referred_mobile: str
    feedback: Optional[str]
