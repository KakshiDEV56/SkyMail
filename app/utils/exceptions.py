from fastapi import HTTPException, status


# Custom Exception Classes
class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class PermissionError(Exception):
    """Raised when user lacks required permissions."""
    pass


# HTTP Exceptions
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"}
    )
