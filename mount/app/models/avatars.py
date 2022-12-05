from datetime import datetime
from enum import Enum

from . import BaseModel


class Breakpoint(str, Enum):
    ORIGINAL = "original"
    THUMBNAIL = "thumbnail"

    # https://tailwindcss.com/docs/responsive-design
    # https://vuetifyjs.com/en/features/breakpoints
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"


# input models

# output models
class Avatar(BaseModel):
    id: int
    account_id: int
    breakpoint: Breakpoint
    content_type: str
    width: int
    height: int
    filesize: int
    status: str
    created_at: datetime
    updated_at: datetime
