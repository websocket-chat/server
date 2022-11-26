from datetime import datetime
from uuid import UUID

from . import BaseModel


# input models


class LoginForm(BaseModel):
    username: str
    password: str


# output models
class Session(BaseModel):
    session_id: UUID
    account_id: int
    user_agent: str
    # expires_at: str
    created_at: datetime
    updated_at: datetime
