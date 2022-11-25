def dsn(
    db_driver: str,
    db_host: str,
    db_port: int,
    db_user: str,
    db_pass: str,
    db_name: str,
) -> str:
    return f"{db_driver}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
