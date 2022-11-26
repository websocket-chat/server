import email_validator


def validate_username(username: str) -> bool:
    return 3 <= len(username) <= 16


def validate_password(password: str) -> bool:
    if not 8 <= len(password) <= 128:
        return False

    if not any(c.isupper() for c in password):
        return False

    if not any(c.islower() for c in password):
        return False

    if not any(c.isdigit() for c in password):
        return False

    return True


def validate_email(email: str) -> bool:
    try:
        # TODO: asynchronize the deliverability checks?
        email_validator.validate_email(email)
    except email_validator.EmailNotValidError as e:
        return False
    else:
        return True
