from datetime import datetime
from app.services.membership_service import generate_membership_id
from app.schemas.admin_bulk import BulkUserActionRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse

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
from app.models.user_pending import UserPending
from app.models.user_rejected import UserRejected
from app.models.admin_audit_log import AdminAuditLog
from fastapi import BackgroundTasks
from app.api.admin_permissions import require_roles

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
        query = query.filter(UserPending.current_state == state)

    if district:
        query = query.filter(UserPending.current_district == district)

    if mandal:
        query = query.filter(UserPending.current_mandal == mandal)

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
    require_roles(current_admin, ["super_admin", "verifier"])
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
        query = query.filter(UserPending.current_state == state)

    if desired_name:
        query = query.filter(UserPending.desired_name.ilike(f"%{desired_name}%"))

    if district:
        query = query.filter(UserPending.current_district == district)

    if mandal:
        query = query.filter(UserPending.current_mandal == mandal)

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
    registration_id: Optional[str] = None,

    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    
    require_roles(current_admin, ["super_admin", "verifier"])
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
        query = query.filter(UserVerified.current_state == state)


    if district:
        query = query.filter(UserVerified.current_district == district)

    if mandal:
        query = query.filter(UserVerified.current_mandal == mandal)
    if registration_id:
        query = query.filter(UserVerified.registration_id == registration_id)

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
    require_roles(current_admin, ["super_admin", "verifier"])
    user = db.query(UserPending).filter(UserPending.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


from app.models.user_verified import UserVerified

@router.post("/user/{user_id}/approve")
def approve_user(user_id: str, 
                 background_tasks: BackgroundTasks,
                 db: Session = Depends(get_db),current_admin: dict = Depends(get_current_admin)):
    
    require_roles(current_admin, ["super_admin", "verifier"])
    user = db.query(UserPending).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.status != "pending":
        raise HTTPException(400, "User not in pending state")

    membership_id = generate_membership_id(db)

    verified = UserVerified(
        membership_id=membership_id,
        registration_id=user.registration_id,
          # ✅ ADD THIS
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
        marital_status=user.marital_status,
        blood_group=user.blood_group,
        gothram=user.gothram,
        aaradhya_daiva=user.aaradhya_daiva,
        kula_devata=user.kula_devata,
        education=user.education,
        occupation=user.occupation,
        # Current Address
        current_house_number=user.current_house_number,
        current_village_city=user.current_village_city,
        current_mandal=user.current_mandal,
        current_district=user.current_district,
        current_state=user.current_state,
        current_country=user.current_country,
        current_pin_code=user.current_pin_code,
        # Native Address    
        native_house_number=user.native_house_number,
        native_village_city=user.native_village_city,
        native_mandal=user.native_mandal,
        native_district=user.native_district,
        native_state=user.native_state,
        native_country=user.native_country,
        native_pin_code=user.native_pin_code,
        # Photo
        photo_url=user.photo_url,
        pdf_url=user.pdf_url,
        referred_by_name=user.referred_by_name,
        referred_mobile=user.referred_mobile,
        feedback=user.feedback,

        # Approval Info
        approved_by=current_admin.get("sub"),
        approved_at=datetime.utcnow()
    )

    try:
        db.add(verified)

         # ✅ ADD AUDIT LOG ENTRY
        audit = AdminAuditLog(
                    admin_id=current_admin.get("sub"),
                    action="APPROVE",
                    target_type="user",
                    target_id=user.id
                )
        
        background_tasks.add_task(
        send_approval_email,
        user.email,
        user.desired_name or user.full_name,
        membership_id
        )

        

        db.add(audit)
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, "Approval failed")


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
    registration_id: Optional[str] = None,

    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    
    require_roles(current_admin, ["super_admin", "verifier"])
    # =========================
    # BASE QUERY (ALL STATUSES)
    # =========================
    query = db.query(UserPending)

    # =========================
    # FILTERS
    # =========================
    if state:
        query = query.filter(UserPending.current_state == state)

    if district:
        query = query.filter(UserPending.current_district == district)

    if mandal:
        query = query.filter(UserPending.current_mandal == mandal)

    if gothram:
        query = query.filter(UserPending.gothram.ilike(f"%{gothram}%"))

    if surname:
        query = query.filter(UserPending.surname == surname)

    if registration_id:
        query = query.filter(UserPending.registration_id == registration_id)    

    users = query.order_by(UserPending.created_at.desc()).all()

    # =========================
    # CSV GENERATION
    # =========================
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        
        "Registration ID",
        "Full Name",
        "Mothers Maiden Name as Surname",
        "Gothram",
        "Mobile",
        "Email",
        "Current Address",
        "Current State",
        "Current District",
        "Current Mandal",
        "Current Pincode",
        "Status",
        "Registered Date",
        "Approved Date"
    ])

    for user in users:
        writer.writerow([
            
            getattr(user, "registration_id", ""),
            getattr(user, "full_name", ""),
            getattr(user, "surname", ""),
            getattr(user, "gothram", ""),
            getattr(user, "mobile_number", ""),
            getattr(user, "email", ""),
            #getattr(user, "current_house_number", "") + " " + getattr(user, "current_village_city", ""),
            f"{user.current_house_number or ''} {user.current_village_city or ''}".strip(),

            getattr(user, "current_state", ""),
            getattr(user, "current_district", ""),
            getattr(user, "current_mandal", ""),
            getattr(user, "current_pin_code", ""),
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    
    require_roles(current_admin, ["super_admin", "verifier"])

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
                registration_id=user.registration_id,
                verification_type=user.verification_type,
                mobile_number=user.mobile_number,
                email=user.email,
                full_name=user.full_name,
                surname=user.surname, # Mothers Maiden Name as Surname
                desired_name=user.desired_name,
                father_or_husband_name=user.father_or_husband_name,
                mother_name=user.mother_name,
                date_of_birth=user.date_of_birth,
                gender=user.gender,
                marital_status=user.marital_status,
                blood_group=user.blood_group,
                gothram=user.gothram,
                aaradhya_daiva=user.aaradhya_daiva,
                kula_devata=user.kula_devata,
                education=user.education,
                occupation=user.occupation,
                # Current Address
                current_house_number=user.current_house_number,
                current_village_city=user.current_village_city,
                current_mandal=user.current_mandal,
                current_district=user.current_district,
                current_state=user.current_state,
                current_country=user.current_country,
                current_pin_code=user.current_pin_code,
                # Native Address
                native_house_number=user.native_house_number,
                native_village_city=user.native_village_city,
                native_mandal=user.native_mandal,
                native_district=user.native_district,
                native_state=user.native_state,
                native_country=user.native_country,
                native_pin_code=user.native_pin_code,
                # Photo
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
                            
                            
                            background_tasks.add_task(
                send_approval_email,
                user.email,
                user.desired_name or user.full_name,
                membership_id
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





# @router.post("/users/bulk-reject")
# def bulk_reject_users(
#     payload: BulkUserActionRequest,
#     db: Session = Depends(get_db),
#     current_admin: dict = Depends(get_current_admin)
# ):
#     if not payload.reason:
#         raise HTTPException(status_code=400, detail="Reject reason required")

#     users = (
#         db.query(UserPending)
#         .filter(
#             UserPending.id.in_(payload.user_ids),
#             UserPending.status == "pending"
#         )
#         .all()
#     )

#     if len(users) != len(payload.user_ids):
#         raise HTTPException(status_code=400, detail="Invalid selection")

#     for user in users:
#         user.status = "rejected"
#         user.reject_reason = payload.reason

#         # 🔹 Send rejection email (only if email exists)
#         if user.email:
#             send_rejection_email(
#                 to_email=user.email,
#                 full_name=user.full_name,
#                 desired_name=user.desired_name,
#                 reason=payload.reason
#             )
        
#         # ADD AUDIT LOG ENTRY PER USER
#         audit = AdminAuditLog(
#         admin_id=current_admin.get("sub"),
#         action="REJECT",
#         target_type="user",
#         target_id=user.id,
#         reason=payload.reason
#         )
#         db.add(audit)

    


#     db.commit()

#     return {
#         "message": f"{len(users)} users rejected and via email notified"
#     }

@router.post("/users/bulk-reject")
def bulk_reject_users(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    require_roles(current_admin, ["super_admin", "verifier"])
    if not payload.reason:
        raise HTTPException(status_code=400, detail="Reject reason required")

    # users = (
    #     db.query(UserPending)
    #     .filter(
    #         UserPending.id.in_(payload.user_ids),
    #         UserPending.status == "pending"
    #     )
    #     .all()
    # )

    users = (
    db.query(UserPending)
    .filter(
        UserPending.status == "pending",
        UserPending.id.in_(payload.user_ids[:10000])
    )
    .all()
    )

    for user in users:
        if user.status != "pending":
            raise HTTPException(status_code=400, detail="Some users are not in pending state")



    if len(users) != len(payload.user_ids):
        raise HTTPException(status_code=400, detail="Invalid selection")

    for user in users:
        # 1️⃣ MOVE TO users_rejected
        rejected_user = UserRejected(
            original_pending_id=user.id,
            registration_id=user.registration_id,
            mobile_number=user.mobile_number,
            email=user.email,
            full_name=user.full_name,
            surname=user.surname,  # Mothers Maiden Name as Surname
            desired_name=user.desired_name,
            father_or_husband_name=user.father_or_husband_name,
            mother_name=user.mother_name,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            blood_group=user.blood_group,
            marital_status=user.marital_status,
            # Community
            gothram=user.gothram,
            aaradhya_daiva=user.aaradhya_daiva,
            kula_devata=user.kula_devata,
            education=user.education,
            occupation=user.occupation,
            # Current Address
            current_house_number=user.current_house_number,
            current_village_city=user.current_village_city,
            current_mandal=user.current_mandal,
            current_district=user.current_district,
            current_state=user.current_state,
            current_country=user.current_country,
            current_pin_code=user.current_pin_code,
            # Native Address
            native_house_number=user.native_house_number,
            native_village_city=user.native_village_city,
            native_mandal=user.native_mandal,
            native_district=user.native_district,
            native_state=user.native_state,
            native_country=user.native_country,
            native_pin_code=user.native_pin_code,
            # Photo
            photo_url=user.photo_url,
            # Referral
            referred_by_name=user.referred_by_name,
            referred_mobile=user.referred_mobile,
            reject_reason=payload.reason,
            rejected_by_admin_id=current_admin.get("sub"),
            created_at=user.created_at
        )

        db.add(rejected_user)

        # 2️⃣ AUDIT LOG
        audit = AdminAuditLog(
            admin_id=current_admin.get("sub"),
            action="REJECT",
            target_type="user",
            target_id=user.id,
            reason=payload.reason
        )
        db.add(audit)

        # 3️⃣ SEND REJECTION EMAIL (if email exists)
        if user.email:
            send_rejection_email(
                to_email=user.email,
                full_name=user.full_name,
                regisration_id=user.registration_id,
                desired_name=user.desired_name,
                reason=payload.reason
            )

        # 4️⃣ REMOVE FROM users_pending
        db.delete(user)

    db.commit()

    return {
        "message": f"{len(users)} users rejected and notified successfully"
    }



@router.post("/users/bulk-hold")
def bulk_hold_users(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    require_roles(current_admin, ["super_admin", "verifier"])
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

    for user in users:
        if user.status != "pending":
            raise HTTPException(status_code=400, detail="Some users are not in pending state")

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
    
    require_roles(current_admin, ["super_admin", "verifier"])
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

    # rejected_count = (
    #     db.query(func.count())
    #     .select_from(UserPending)
    #     .filter(UserPending.status == "rejected")
    #     .scalar()
    # )

    rejected_count = (
    db.query(func.count())
    .select_from(UserRejected)
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
    require_roles(current_admin, ["super_admin", "verifier"])
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
        "Registration ID",
        "Full Name",
        "Mothers Maiden Name as Surname",
        "Desired Name",
        "Gothram",
        "Mobile",
        "Email",
        "Current House No",
        "Current Village / City",
        "Current Mandal",
        "Current District",
        "Current State",
        "Current Country",
        "Current Pincode",
        "Approved By",
        "Approved Date"
    ])

    # =========================
    # CSV ROWS
    # =========================
    for user in users:
        writer.writerow([
            user.membership_id,
            user.registration_id,
            user.full_name,
            user.surname,
            user.desired_name,
            user.gothram,
            user.mobile_number,
            user.email,
            user.current_house_number,
            user.current_village_city,
            user.current_mandal,
            user.current_district,
            user.current_state,
            user.current_country,
            user.current_pin_code,
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
