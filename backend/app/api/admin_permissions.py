from fastapi import HTTPException

def require_roles(current_admin: dict, allowed_roles: list[str]):
    if current_admin.get("role") not in allowed_roles:
        raise HTTPException(status_code=403, detail="Unauthorized")
