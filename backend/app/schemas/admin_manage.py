from pydantic import BaseModel
from typing import Optional

class AdminCreateRequest(BaseModel):
    username: str
    password: str
    role: str


class AdminUpdateRoleRequest(BaseModel):
    role: str


class AdminResetPasswordRequest(BaseModel):
    new_password: str
