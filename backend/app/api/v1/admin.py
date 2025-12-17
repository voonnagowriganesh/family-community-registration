from datetime import datetime
from app.services.membership_service import generate_membership_id
from app.schemas.admin_bulk import BulkUserActionRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse
from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token
from app.models.admin_user import AdminUser
from app.models.user_verified import UserVerified
from app.api.deps import get_db
from app.api.deps import get_current_admin
import io
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from app.models.admin_audit_log import AdminAuditLog
from app.services.email_service import send_approval_email
from app.services.email_service import send_rejection_email

#---
from datetime import date
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["Admin"])


def build_user_query(
    db: Session,
    status: str,
    state: str | None = None,
    district: str | None = None,
    mandal: str | None = None,
    gothram: str | None = None,
    surname: str | None = None,
):
    query = db.query(UserPending).filter(UserPending.status == status)

    if state:
        query = query.filter(UserPending.state == state)

    if district:
        query = query.filter(UserPending.district == district)

    if mandal:
        query = query.filter(UserPending.mandal == mandal)

    if gothram:
        query = query.filter(UserPending.gothram.ilike(f"%{gothram}%"))

    if surname:
        query = query.filter(UserPending.surname == surname)

    return query


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(
    data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    admin = db.query(AdminUser).filter(AdminUser.username == data.username).first()

    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(admin.id),
        "role": admin.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }



from sqlalchemy import and_
from app.models.user_pending import UserPending
from typing import Optional



# @router.get("/pending-users")
# def get_pending_users(
#     current_admin: dict = Depends(get_current_admin),
#     state: str = None,
#     district: str = None,
#     mandal: str = None,
#     gothram: str = None,
#     surname: str = None,
#     verification_type: str = None,
#     possible_duplicate: bool = None,
#     search: str = None,
#     db: Session = Depends(get_db)
# ):
#     query = db.query(UserPending)

#     if state:
#         query = query.filter(UserPending.state == state)
#     if district:
#         query = query.filter(UserPending.district == district)
#     if mandal:
#         query = query.filter(UserPending.mandal == mandal)
#     if gothram:
#         query = query.filter(UserPending.gothram.ilike(f"%{gothram}%"))
#     if surname:
#         query = query.filter(UserPending.surname == surname)
#     if verification_type:
#         query = query.filter(UserPending.verification_type == verification_type)
#     if possible_duplicate is not None:
#         query = query.filter(UserPending.possible_duplicate == possible_duplicate)
#     if search:
#         query = query.filter(
#             UserPending.full_name.ilike(f"%{search}%") |
#             UserPending.mobile_number.ilike(f"%{search}%") |
#             UserPending.email.ilike(f"%{search}%")
#         )

#     return query.order_by(UserPending.created_at.desc()).all()



@router.get("/pending-users")
def get_pending_users(
    page: int = 1,
    size: int = 20,

    # Filters
    desired_name: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    mandal: Optional[str] = None,
    gothram: Optional[str] = None,
    surname: Optional[str] = None,

    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # =========================
    # PAGINATION GUARDS
    # =========================
    MAX_PAGE_SIZE = 100

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    if size < 1 or size > MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Size must be between 1 and {MAX_PAGE_SIZE}"
        )

    # =========================
    # BASE QUERY (ONLY PENDING)
    # =========================
    query = db.query(UserPending).filter(UserPending.status == "pending")

    # =========================
    # FILTERS
    # =========================
    if state:
        query = query.filter(UserPending.state == state)

    if desired_name:
        query = query.filter(UserVerified.desired_name.ilike(f"%{desired_name}%"))

    if district:
        query = query.filter(UserPending.district == district)

    if mandal:
        query = query.filter(UserPending.mandal == mandal)

    if gothram:
        query = query.filter(UserPending.gothram.ilike(f"%{gothram}%"))

    if surname:
        query = query.filter(UserPending.surname == surname)

    # =========================
    # TOTAL COUNT
    # =========================
    total_records = query.count()

    # =========================
    # PAGINATION
    # =========================
    offset = (page - 1) * size

    users = (
        query
        .order_by(UserPending.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    total_pages = (total_records + size - 1) // size

    # =========================
    # RESPONSE
    # =========================
    return {
        "page": page,
        "size": size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": users
    }


@router.get("/approved-users")
def get_approved_users(
    page: int = 1,
    size: int = 20,
    # Filters
    surname: Optional[str] = None,
    gothram: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    mandal: Optional[str] = None,

    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # =========================
    # PAGINATION GUARDS
    # =========================
    MAX_PAGE_SIZE = 100

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")

    if size < 1 or size > MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Size must be between 1 and {MAX_PAGE_SIZE}"
        )

    # =========================
    # BASE QUERY (IMPORTANT)
    # =========================
    query = db.query(UserVerified)

    # =========================
    # FILTERS
    # =========================
    if surname:
        query = query.filter(UserVerified.surname == surname)

    if gothram:
        query = query.filter(UserVerified.gothram.ilike(f"%{gothram}%"))

    if state:
        query = query.filter(UserVerified.state == state)

    if district:
        query = query.filter(UserVerified.district == district)

    if mandal:
        query = query.filter(UserVerified.mandal == mandal)

    # =========================
    # TOTAL COUNT
    # =========================
    total_records = query.count()

    # =========================
    # PAGINATION
    # =========================
    offset = (page - 1) * size

    users = (
        query
        .order_by(UserVerified.approved_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    total_pages = (total_records + size - 1) // size

    # =========================
    # RESPONSE
    # =========================
    return {
        "page": page,
        "size": size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": users
    }




@router.get("/user/{user_id}")
def get_user_detail(user_id: str, db: Session = Depends(get_db),current_admin: dict = Depends(get_current_admin)):
    user = db.query(UserPending).filter(UserPending.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


from app.models.user_verified import UserVerified

@router.post("/user/{user_id}/approve")
def approve_user(user_id: str, db: Session = Depends(get_db),current_admin: dict = Depends(get_current_admin)):
    user = db.query(UserPending).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    membership_id = generate_membership_id(db)

    verified = UserVerified(
        membership_id=membership_id,
        verification_type=user.verification_type,
        mobile_number=user.mobile_number,
        email=user.email,
        full_name=user.full_name,
        surname=user.surname,
        desired_name=user.desired_name,
        father_or_husband_name=user.father_or_husband_name,
        mother_name=user.mother_name,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        blood_group=user.blood_group,
        gothram=user.gothram,
        aaradhya_daiva=user.aaradhya_daiva,
        kula_devata=user.kula_devata,
        education=user.education,
        occupation=user.occupation,
        house_number=user.house_number,
        village_city=user.village_city,
        mandal=user.mandal,
        district=user.district,
        state=user.state,
        country=user.country,
        pin_code=user.pin_code,
        photo_url=user.photo_url,
        pdf_url=user.pdf_url,
        referred_by_name=user.referred_by_name,
        referred_mobile=user.referred_mobile,
        feedback=user.feedback,
    )

    db.add(verified)
    # ✅ ADD AUDIT LOG ENTRY
    audit = AdminAuditLog(
                admin_id=current_admin.get("sub"),
                action="APPROVE",
                target_type="user",
                target_id=user.id
            )
    db.add(audit)
    db.delete(user)
    db.commit()

    return {
        "message": "User approved successfully",
        "membership_id": membership_id
    }



@router.get("/export-pending-users")
def export_users_csv(
    # Filters (same as pending-users)
    state: Optional[str] = None,
    district: Optional[str] = None,
    mandal: Optional[str] = None,
    gothram: Optional[str] = None,
    surname: Optional[str] = None,

    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # =========================
    # BASE QUERY (ALL STATUSES)
    # =========================
    query = db.query(UserPending)

    # =========================
    # FILTERS
    # =========================
    if state:
        query = query.filter(UserPending.state == state)

    if district:
        query = query.filter(UserPending.district == district)

    if mandal:
        query = query.filter(UserPending.mandal == mandal)

    if gothram:
        query = query.filter(UserPending.gothram.ilike(f"%{gothram}%"))

    if surname:
        query = query.filter(UserPending.surname == surname)

    users = query.order_by(UserPending.created_at.desc()).all()

    # =========================
    # CSV GENERATION
    # =========================
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Membership ID",
        "Full Name",
        "Surname",
        "Gothram",
        "Mobile",
        "Email",
        "Address",
        "State",
        "District",
        "Mandal",
        "Pincode",
        "Status",
        "Registered Date",
        "Approved Date"
    ])

    for user in users:
        writer.writerow([
            getattr(user, "membership_id", ""),
            getattr(user, "full_name", ""),
            getattr(user, "surname", ""),
            getattr(user, "gothram", ""),
            getattr(user, "mobile_number", ""),
            getattr(user, "email", ""),
            getattr(user, "address", ""),
            getattr(user, "state", ""),
            getattr(user, "district", ""),
            getattr(user, "mandal", ""),
            getattr(user, "pincode", ""),
            getattr(user, "status", ""),
            user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            user.approved_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user, "approved_at") and user.approved_at else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users_export.csv"
        }
    )




@router.post("/users/bulk-approve")
def bulk_approve_users(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    if not payload.user_ids:
        raise HTTPException(status_code=400, detail="No users selected")

    users = (
        db.query(UserPending)
        .filter(
            UserPending.id.in_(payload.user_ids),
            UserPending.status == "pending"
        )
        .all()
    )

    if len(users) != len(payload.user_ids):
        raise HTTPException(
            status_code=400,
            detail="Some users are not in pending status"
        )

    try:
        for user in users:
            membership_id = generate_membership_id(db)

            verified_user = UserVerified(
                membership_id=membership_id,
                verification_type=user.verification_type,
                mobile_number=user.mobile_number,
                email=user.email,
                full_name=user.full_name,
                surname=user.surname,
                desired_name=user.desired_name,
                father_or_husband_name=user.father_or_husband_name,
                mother_name=user.mother_name,
                date_of_birth=user.date_of_birth,
                gender=user.gender,
                blood_group=user.blood_group,
                gothram=user.gothram,
                aaradhya_daiva=user.aaradhya_daiva,
                kula_devata=user.kula_devata,
                education=user.education,
                occupation=user.occupation,
                house_number=user.house_number,
                village_city=user.village_city,
                mandal=user.mandal,
                district=user.district,
                state=user.state,
                country=user.country,
                pin_code=user.pin_code,
                photo_url=user.photo_url,
                pdf_url=user.pdf_url,
                referred_by_name=user.referred_by_name,
                referred_mobile=user.referred_mobile,
                feedback=user.feedback,
                approved_by=current_admin.get("sub"),
                approved_at=datetime.utcnow()
            )

            db.add(verified_user)
            
            # ✅ ADD AUDIT LOG ENTRY
            audit = AdminAuditLog(
                admin_id=current_admin.get("sub"),
                action="APPROVE",
                target_type="user",
                target_id=user.id,
                reason=payload.reason
            )
            db.add(audit)


            # 📧 SEND APPROVAL EMAIL (safe)
            try:
                send_approval_email(
                    to_email=user.email,
                    desired_name=user.desired_name or user.full_name,
                    membership_id=membership_id
                )
            except Exception as e:
                print("EMAIL ERROR:", str(e))  # do NOT fail approval

            db.delete(user)

        db.commit()

    except Exception as e:
        db.rollback()
        print("BULK APPROVE ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


    return {
        "message": f"{len(users)} users approved successfully"
    }





@router.post("/users/bulk-reject")
def bulk_reject_users(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    if not payload.reason:
        raise HTTPException(status_code=400, detail="Reject reason required")

    users = (
        db.query(UserPending)
        .filter(
            UserPending.id.in_(payload.user_ids),
            UserPending.status == "pending"
        )
        .all()
    )

    if len(users) != len(payload.user_ids):
        raise HTTPException(status_code=400, detail="Invalid selection")

    for user in users:
        user.status = "rejected"
        user.reject_reason = payload.reason

        # 🔹 Send rejection email (only if email exists)
        if user.email:
            send_rejection_email(
                to_email=user.email,
                full_name=user.full_name,
                desired_name=user.desired_name,
                reason=payload.reason
            )
        
        # ADD AUDIT LOG ENTRY PER USER
        audit = AdminAuditLog(
        admin_id=current_admin.get("sub"),
        action="REJECT",
        target_type="user",
        target_id=user.id,
        reason=payload.reason
        )
        db.add(audit)

    


    db.commit()

    return {
        "message": f"{len(users)} users rejected and via email notified"
    }




@router.post("/users/bulk-hold")
def bulk_hold_users(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    if not payload.reason:
        raise HTTPException(status_code=400, detail="Hold reason required")

    users = (
        db.query(UserPending)
        .filter(
            UserPending.id.in_(payload.user_ids),
            UserPending.status == "pending"
        )
        .all()
    )

    if len(users) != len(payload.user_ids):
        raise HTTPException(status_code=400, detail="Invalid selection")

    for user in users:
        user.status = "hold"
        user.hold_reason = payload.reason
        # ADD AUDIT LOG ENTRY PER USER
        audit = AdminAuditLog(
        admin_id=current_admin.get("sub"),
        action="HOLD",
        target_type="user",
        target_id=user.id,
        reason=payload.reason
        )
        db.add(audit)


    db.commit()

    return {
        "message": f"{len(users)} users moved to hold"
    }



@router.get("/dashboard/summary")
def admin_dashboard_summary(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    today = date.today()

    # =========================
    # STATUS COUNTS
    # =========================

    pending_count = (
        db.query(func.count())
        .select_from(UserPending)
        .filter(UserPending.status == "pending")
        .scalar()
    )

    hold_count = (
        db.query(func.count())
        .select_from(UserPending)
        .filter(UserPending.status == "hold")
        .scalar()
    )

    rejected_count = (
        db.query(func.count())
        .select_from(UserPending)
        .filter(UserPending.status == "rejected")
        .scalar()
    )

    approved_count = (
        db.query(func.count())
        .select_from(UserVerified)
        .scalar()
    )

    total_registrations = (
        pending_count + hold_count + rejected_count + approved_count
    )

    # =========================
    # TODAY ACTIVITY
    # =========================

    today_registrations = (
        db.query(func.count())
        .select_from(UserPending)
        .filter(func.date(UserPending.created_at) == today)
        .scalar()
    )

    today_approvals = (
        db.query(func.count())
        .select_from(UserVerified)
        .filter(func.date(UserVerified.approved_at) == today)
        .scalar()
    )

    today_rejections = (
        db.query(func.count())
        .select_from(UserPending)
        .filter(
            UserPending.status == "rejected",
            func.date(UserPending.created_at) == today
        )
        .scalar()
    )

    # =========================
    # RESPONSE
    # =========================

    return {
        "summary": {
            "total_registrations": total_registrations,
            "approved": approved_count,
            "pending": pending_count,
            "hold": hold_count,
            "rejected": rejected_count
        },
        "today": {
            "new_registrations": today_registrations,
            "approvals": today_approvals,
            "rejections": today_rejections
        }
    }



@router.get("/export-approved-users")
def export_approved_users(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # =========================
    # FETCH APPROVED USERS
    # =========================
    users = (
        db.query(UserVerified)
        .order_by(UserVerified.approved_at.desc())
        .all()
    )

    # =========================
    # CSV IN-MEMORY BUFFER
    # =========================
    output = io.StringIO()
    writer = csv.writer(output)

    # =========================
    # CSV HEADER
    # =========================
    writer.writerow([
        "Membership ID",
        "Full Name",
        "Surname",
        "Desired Name",
        "Gothram",
        "Mobile",
        "Email",
        "House No",
        "Village / City",
        "Mandal",
        "District",
        "State",
        "Country",
        "Pincode",
        "Approved By",
        "Approved Date"
    ])

    # =========================
    # CSV ROWS
    # =========================
    for user in users:
        writer.writerow([
            user.membership_id,
            user.full_name,
            user.surname,
            user.desired_name,
            user.gothram,
            user.mobile_number,
            user.email,
            user.house_number,
            user.village_city,
            user.mandal,
            user.district,
            user.state,
            user.country,
            user.pin_code,
            user.approved_by,
            user.approved_at
        ])

    output.seek(0)

    # =========================
    # STREAM RESPONSE
    # =========================
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=approved_users.csv"
        }
    )
