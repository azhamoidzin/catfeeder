from enum import StrEnum
from fastapi.security import OAuth2PasswordBearer


class RoutesEnum(StrEnum):
    LOGIN = 'login'
    REGISTER = 'register'
    ACTIVATE = 'activate'
    USERS = 'users'
    FEEDERS = 'feeders'
    TIME_SIMULATION = 'time'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=RoutesEnum.LOGIN)
