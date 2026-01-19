from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions

ph = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return ph.hash(plain_password)


def verify_password(
    hashed_password: str,
    plain_password: str,
) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except (
        argon2_exceptions.VerifyMismatchError,
        argon2_exceptions.InvalidHashError,
        argon2_exceptions.Argon2Error,
    ):
        pass
    return False
