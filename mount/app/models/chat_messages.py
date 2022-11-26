from . import BaseModel

# input models


class SendChatMessage(BaseModel):
    message_content: str
    target_account_id: int


# output models
