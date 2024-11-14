from passlib.context import CryptContext
from app.global_config import CRYPT_SCHEME

pwd_context = CryptContext(schemes=[CRYPT_SCHEME], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
