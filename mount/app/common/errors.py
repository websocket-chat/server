from enum import Enum


class ServiceError(str, Enum):
    ACCOUNTS_SIGNUP_FAILED = "accounts.signup_failed"
    ACCOUNTS_DELETION_FAILED = "accounts.deletion_failed"
    ACCOUNTS_NOT_FOUND = "accounts.not_found"
    ACCOUNTS_USERNAME_INVALID = "accounts.username_invalid"
    ACCOUNTS_PASSWORD_INVALID = "accounts.password_invalid"
    ACCOUNTS_EMAIL_ADDRESS_INVALID = "accounts.email_address_invalid"
    ACCOUNTS_EMAIL_ADDRESS_EXISTS = "accounts.email_address_exists"
    ACCOUNTS_USERNAME_EXISTS = "accounts.username_exists"

    SESSIONS_NOT_FOUND = "sessions.not_found"

    CREDENTIALS_NOT_FOUND = "credentials.incorrect_credentials"
    CREDENTIALS_INCORRECT = "credentials.incorrect_credentials"

    AVATARS_CREATION_FAILED = "avatars.creation_failed"
    AVATARS_DELETION_FAILED = "avatars.deletion_failed"
    AVATARS_NOT_FOUND = "avatars.not_found"
    AVATARS_CONTENT_TYPE_INVALID = "avatars.content_type_invalid"
    AVATARS_SIZE_TOO_LARGE = "avatars.size_too_large"
