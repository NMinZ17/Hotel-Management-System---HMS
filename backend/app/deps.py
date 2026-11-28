"""Current-user dependency and role checks, enforced at the API layer."""

from dataclasses import dataclass, field

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import get_db
from app.errors import forbidden, unauthorized
from app.security import decode_token

STAFF_ROLES = frozenset({"ADMIN", "RECEPTION", "STAFF"})

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: int
    email: str
    roles: frozenset[str] = field(default_factory=frozenset)
    guest_id: int | None = None
    employee_id: int | None = None
    full_name: str | None = None

    @property
    def is_staff(self) -> bool:
        return bool(self.roles & STAFF_ROLES)


USER_SQL = """
    SELECT u.user_id, u.email, u.is_active,
           g.guest_id, g.full_name AS guest_name,
           e.employee_id, e.full_name AS employee_name,
           COALESCE(
               (SELECT array_agg(r.code ORDER BY r.code)
                FROM user_role ur JOIN role r ON r.role_id = ur.role_id
                WHERE ur.user_id = u.user_id), ARRAY[]::varchar[]
           ) AS roles
    FROM app_user u
    LEFT JOIN guest g ON g.user_id = u.user_id
    LEFT JOIN employee e ON e.user_id = u.user_id AND e.is_active IS TRUE
    WHERE u.user_id = %(user_id)s
    ORDER BY g.guest_id, e.employee_id
    LIMIT 1
"""


def load_user(connection, user_id: int) -> CurrentUser | None:
    row = connection.execute(USER_SQL, {"user_id": user_id}).fetchone()
    if row is None or row["is_active"] is not True:
        return None
    return CurrentUser(
        user_id=row["user_id"],
        email=row["email"],
        roles=frozenset(row["roles"]),
        guest_id=row["guest_id"],
        employee_id=row["employee_id"],
        full_name=row["guest_name"] or row["employee_name"],
    )


def current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if credentials is None:
        raise unauthorized()
    secret = request.app.state.settings.auth_secret
    user_id = decode_token(credentials.credentials, secret) if secret else None
    if user_id is None:
        raise unauthorized("Phiên đăng nhập không hợp lệ hoặc đã hết hạn.")
    with get_db(request) as connection:
        user = load_user(connection, user_id)
    if user is None:
        raise unauthorized("Tài khoản không tồn tại hoặc đã bị khóa.")
    return user


def require_guest(user: CurrentUser = Depends(current_user)) -> CurrentUser:
    if "GUEST" not in user.roles or user.guest_id is None:
        raise forbidden("Chỉ tài khoản khách mới đặt hoặc hủy phòng của mình.")
    return user


def require_staff(user: CurrentUser = Depends(current_user)) -> CurrentUser:
    if not user.is_staff or user.employee_id is None:
        raise forbidden("Chỉ nhân viên được phân quyền mới thực hiện được thao tác này.")
    return user
