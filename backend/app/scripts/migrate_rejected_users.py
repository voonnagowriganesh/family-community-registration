from app.core.database import SessionLocal
from app.models.user_pending import UserPending
from app.models.user_rejected import UserRejected

db = SessionLocal()

try:
    rejected_users = (
        db.query(UserPending)
        .filter(UserPending.status == "rejected")
        .all()
    )

    print(f"Found {len(rejected_users)} rejected users")

    for user in rejected_users:
        rejected = UserRejected(
            original_pending_id=user.id,
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
            referred_by_name=user.referred_by_name,
            referred_mobile=user.referred_mobile,
            reject_reason=user.reject_reason,
            created_at=user.created_at
        )

        db.add(rejected)
        db.delete(user)

    db.commit()
    print("✅ Migration completed successfully")

except Exception as e:
    db.rollback()
    print("❌ Migration failed:", str(e))

finally:
    db.close()
