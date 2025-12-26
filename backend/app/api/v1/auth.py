from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.otp_service import generate_otp, get_expiry_time
from app.models.otp_verification import OTPVerification
from app.api.deps import get_db
from app.services.sms_service import send_otp_sms
from app.services.email_service import send_otp_email
from app.models.user_pending import UserPending
from app.models.user_verified import UserVerified
from fastapi import BackgroundTasks

from app.services.otp_cleanup_service import cleanup_expired_otps


router = APIRouter(prefix="/auth")

# =========================
# REQUEST SCHEMAS
# =========================

class SendOTPRequest(BaseModel):
    type: str  # mobile | email
    value: str

class VerifyOTPRequest(BaseModel):
    type: str
    value: str
    otp: str

# =========================
# SEND OTP
# =========================

# @router.post("/send-otp")
# def send_otp(payload: SendOTPRequest, db: Session = Depends(get_db)):
#     if payload.type not in ["mobile", "email"]:
#         raise HTTPException(status_code=400, detail="Invalid verification type")

#     otp = generate_otp()
#     expiry = get_expiry_time()

#     otp_entry = OTPVerification(
#         identifier=payload.value,
#         verification_type=payload.type,
#         otp=otp,
#         expires_at=expiry
#     )

#     db.add(otp_entry)
#     db.commit()

#     # 🔐 SEND REAL OTP
#     if payload.type == "mobile":
#         send_otp_sms(payload.value, otp)

#     elif payload.type == "email":
#         send_otp_email(payload.value, otp)
#         # 🔴 leave email empty for now
#     return {
#         "message": f"OTP sent successfully via {payload.type}"
#     }

    # # MOCKED RESPONSE (for dev only)
    # return {
    #     "message": f"OTP sent successfully via {payload.type}",
    #     "otp_debug": otp  # ⚠️ REMOVE IN PRODUCTION
    # }


@router.post("/send-otp")
def send_otp(payload: SendOTPRequest, 
             background_tasks: BackgroundTasks,
             db: Session = Depends(get_db)):
    
    # 🧹 CLEAN EXPIRED OTPs FIRST
    cleanup_expired_otps(db)
    

    if payload.type not in ["mobile", "email"]:
        raise HTTPException(status_code=400, detail="Invalid verification type")
    
    
    # 🚫 BLOCK OTP IF USER ALREADY REGISTERED (PENDING / VERIFIED)
    if payload.type == "mobile":
        exists_pending = db.query(UserPending).filter(
            UserPending.mobile_number == payload.value
        ).first()
        exists_verified = db.query(UserVerified).filter(
            UserVerified.mobile_number == payload.value
        ).first()

    elif payload.type == "email":
        exists_pending = db.query(UserPending).filter(
            UserPending.email == payload.value
        ).first()
        exists_verified = db.query(UserVerified).filter(
            UserVerified.email == payload.value
        ).first()

    else:
        raise HTTPException(status_code=400, detail="Invalid verification type")

    if exists_pending:
        raise HTTPException(
            status_code=400,
            detail="Registration already submitted. Please wait for admin approval."
        )

    if exists_verified:
        raise HTTPException(
            status_code=400,
            detail="User already registered and approved."
        )

        

        



    # 1️⃣ FETCH LATEST UNVERIFIED OTP
    last_otp = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.identifier == payload.value,
            OTPVerification.verification_type == payload.type,
            OTPVerification.verified == False
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    # 2️⃣ COOLDOWN CHECK (60 seconds)
    if last_otp:
        seconds_since_last = (datetime.utcnow() - last_otp.created_at).total_seconds()
        if seconds_since_last < 60:
            raise HTTPException(
                status_code=429,
                detail="Please wait 60 seconds before requesting another OTP"
            )
    
    


    # 3️⃣ GENERATE OTP
    otp = generate_otp()
    expiry = get_expiry_time()

    otp_entry = OTPVerification(
        identifier=payload.value,
        verification_type=payload.type,
        otp=otp,
        expires_at=expiry
    )

    db.add(otp_entry)
    db.commit()

    # 4️⃣ SEND OTP
    if payload.type == "mobile":
        #send_otp_sms(payload.value, otp)
        background_tasks.add_task(send_otp_sms, payload.value, otp)

    elif payload.type == "email":
        #send_otp_email(payload.value, otp)
        background_tasks.add_task(send_otp_email, payload.value, otp)

    return {
        "message": f"OTP sent successfully via {payload.type}"
    }


# =========================
# VERIFY OTP
# =========================

# @router.post("/verify-otp")
# def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
#     otp_record = (
#         db.query(OTPVerification)
#         .filter(
#             OTPVerification.identifier == payload.value,
#             OTPVerification.verification_type == payload.type,
#             OTPVerification.verified == False
#         )
#         .order_by(OTPVerification.created_at.desc())
#         .first()
#     )

#     if not otp_record:
#         raise HTTPException(status_code=404, detail="OTP not found")

#     if otp_record.expires_at < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="OTP expired")

#     if otp_record.otp != payload.otp:
#         otp_record.attempts += 1
#         db.commit()
#         raise HTTPException(status_code=400, detail="Invalid OTP")

#     otp_record.verified = True
#     db.commit()

#     return {
#         "message": "OTP verified successfully",
#         "verified": True
#     }



MAX_OTP_ATTEMPTS = 5

@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.identifier == payload.value,
            OTPVerification.verification_type == payload.type,
            OTPVerification.verified == False
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(status_code=404, detail="OTP not found")

    # 🔒 Check max attempts
    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(
            status_code=400,
            detail="OTP locked due to too many failed attempts. Please request a new OTP."
        )

    # ⏱ Check expiry
    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    # ❌ Wrong OTP
    if otp_record.otp != payload.otp:
        otp_record.attempts += 1
        db.commit()

        remaining = MAX_OTP_ATTEMPTS - otp_record.attempts
        if remaining <= 0:
            raise HTTPException(
                status_code=400,
                detail="OTP locked due to too many failed attempts. Please request a new OTP."
            )

        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP. {remaining} attempts remaining."
        )

    # ✅ Correct OTP
    otp_record.verified = True
    db.commit()

    return {
        "message": "OTP verified successfully",
        "verified": True
    }
