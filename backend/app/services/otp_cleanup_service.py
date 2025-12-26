from datetime import datetime
from sqlalchemy.orm import Session

from app.models.otp_verification import OTPVerification

def cleanup_expired_otps(db: Session):
    db.query(OTPVerification).filter(
        OTPVerification.expires_at < datetime.utcnow()
    ).delete(synchronize_session=False)

    db.commit()
