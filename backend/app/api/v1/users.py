from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserRegistrationRequest
from app.models.user_pending import UserPending
from app.services.pdf_service import generate_pdf
from app.api.deps import get_db
from app.models.user_verified import UserVerified
import uuid





router = APIRouter(prefix="/users")

@router.post("/register")
def register_user(payload: UserRegistrationRequest, db: Session = Depends(get_db)):

    # =========================
    # NORMALIZE INPUT (CRITICAL)
    # =========================
    mobile_number = payload.mobile_number.strip() if payload.mobile_number else None
    email = payload.email.strip() if payload.email else None
    

    # Convert empty string → None
    mobile_number = mobile_number or None
    email = email or None

    # =========================
    # DUPLICATE CHECK (PENDING)
    # =========================
    if mobile_number:
        if db.query(UserPending).filter(UserPending.mobile_number == mobile_number).first():
            raise HTTPException(
                status_code=400,
                detail="Mobile number already registered, wait for approval/rejection"
            )

    if email:
        if db.query(UserPending).filter(UserPending.email == email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered, wait for approval/rejection"
            )

    # =========================
    # DUPLICATE CHECK (VERIFIED)
    # =========================
    if mobile_number:
        if db.query(UserVerified).filter(UserVerified.mobile_number == mobile_number).first():
            raise HTTPException(
                status_code=400,
                detail="Mobile number already registered and approved"
            )

    if email:
        if db.query(UserVerified).filter(UserVerified.email == email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered and approved"
            )

    # =========================
    # PDF GENERATION
    # =========================
    #pdf_path = generate_pdf(payload.dict(), language="en")
    payload_dict = payload.dict()
    registration_id = f"KGC-{uuid.uuid4().hex[:8].upper()}"
    payload_dict["registration_id"] = registration_id

    pdf_path = generate_pdf(payload_dict, language="en")


    # =========================
    # SAVE USER (SAFE)
    # =========================
    # user = UserPending(
    #     **payload.dict(exclude={"mobile_number", "email"}),
    #     mobile_number=mobile_number,
    #     email=email,
    #     pdf_url=pdf_path,
    #     is_verified=True
    # )

    user = UserPending(
    registration_id=registration_id,   # ✅ ADD HERE
    **payload.dict(exclude={"mobile_number", "email"}),
    mobile_number=mobile_number,
    email=email,
    pdf_url=pdf_path,
    is_verified=True
)


    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration submitted successfully",
        "status": "pending",
        "pdf_url": pdf_path
    }
