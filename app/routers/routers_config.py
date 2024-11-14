from enum import StrEnum
from fastapi.security import OAuth2PasswordBearer


class RoutesEnum(StrEnum):
    _LOGIN = 'login'
    USERS = '/users'
    TIME_SIMULATION = '/time'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=RoutesEnum._LOGIN)
