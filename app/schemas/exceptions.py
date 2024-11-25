from fastapi import HTTPException, status


NOT_ADMIN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You are not admin!",
)

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

INACTIVE_USER = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
)

USER_DOES_NOT_EXIST = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"User does not exist!",
)

USER_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exist",
)

NOT_FAMILY_MEMBER = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User is not member of your family",
)

FEEDER_DOES_NOT_EXIST = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Feeder does not exist!",
)

FEEDER_NOT_CONFIGURED = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="Feeder is not configured yet",
)

OPERATION_NOT_ALLOWED = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    detail="Operation not allowed!",
)
