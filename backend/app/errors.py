from fastapi import HTTPException


class ApiError(HTTPException):
    """Business error with the standard body {"detail": {"code", "message"}}."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(status_code, detail={"code": code, "message": message})


def unauthorized(message: str = "Cần đăng nhập để thực hiện thao tác này.") -> ApiError:
    return ApiError(401, "UNAUTHORIZED", message)


def forbidden(message: str = "Bạn không có quyền thực hiện thao tác này.") -> ApiError:
    return ApiError(403, "FORBIDDEN", message)


def not_found(code: str, message: str) -> ApiError:
    return ApiError(404, code, message)


def conflict(code: str, message: str) -> ApiError:
    return ApiError(409, code, message)


def invalid(code: str, message: str) -> ApiError:
    return ApiError(422, code, message)
