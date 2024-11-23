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
