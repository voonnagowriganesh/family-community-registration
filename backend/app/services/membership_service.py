from sqlalchemy import text
from sqlalchemy.orm import Session

def generate_membership_id(db: Session) -> str:
    result = db.execute(
        text("SELECT nextval('membership_id_seq')")
    ).scalar()

    return f"MEM-{int(result):06d}"
