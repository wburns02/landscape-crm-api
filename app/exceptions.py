from fastapi import HTTPException, status


class CRMException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(CRMException):
    def __init__(self, entity: str = "Resource", id: str | None = None):
        detail = f"{entity} not found" if not id else f"{entity} with id '{id}' not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class AuthError(CRMException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(CRMException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ValidationError(CRMException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
