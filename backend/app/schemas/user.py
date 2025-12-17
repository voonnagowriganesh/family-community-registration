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
    surname: str
    desired_name: str
    father_or_husband_name: str
    mother_name: str
    date_of_birth: Optional[date]

    gender: Optional[str]
    blood_group: Optional[str]

    gothram: str
    aaradhya_daiva: Optional[str]
    kula_devata: Optional[str]

    education: str
    occupation: str

    house_number: Optional[str]
    village_city: str
    mandal: str
    district: str
    state: str
    country: Optional[str] = "India"
    pin_code: str

    photo_url: str

    referred_by_name: str
    referred_mobile: str
    feedback: Optional[str]
