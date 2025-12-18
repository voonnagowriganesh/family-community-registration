from app.core.database import SessionLocal
from app.models.admin_user import AdminUser
from app.core.security import hash_password
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "Admin@123"

db = SessionLocal()

existing_admin = db.query(AdminUser).filter(
    AdminUser.username == ADMIN_EMAIL
).first()

if existing_admin:
    print("Admin already exists")
    
else:
    admin = AdminUser(
        username=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Admin created successfully")

db.close()
