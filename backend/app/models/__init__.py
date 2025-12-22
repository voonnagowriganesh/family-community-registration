# app/models/__init__.py

from app.models.base import Base

# Import ALL models here
from app.models.otp_verification import OTPVerification
from app.models.user_pending import UserPending
from app.models.user_verified import UserVerified
from app.models.admin_audit_log import AdminAuditLog
from app.models.admin_user import AdminUser
from app.models.user_rejected import UserRejected
