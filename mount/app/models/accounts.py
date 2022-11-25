from . import BaseModel

# input models


class SignupForm(BaseModel):
    username: str
    email_address: str
    password: str


# output models
class Account(BaseModel):
    id: int
    username: str
    email_address: str
