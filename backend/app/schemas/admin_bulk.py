from pydantic import BaseModel
from typing import List, Optional

class BulkUserActionRequest(BaseModel):
    user_ids: List[str]
    reason: Optional[str] = None
