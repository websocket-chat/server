from datetime import datetime

from . import BaseModel


# input models


class LoginForm(BaseModel):
    username: str
    password: str


# output models
class Session(BaseModel):
    session_id: str
    account_id: str
    user_agent: str
    # expires_at: str
    created_at: datetime
    updated_at: datetime
