from fastapi import APIRouter, Depends, Request

from app.db import get_db, get_tx
from app.deps import CurrentUser, current_user, load_user
from app.errors import ApiError, conflict, unauthorized
from app.schemas import LoginRequest, RegisterRequest, TokenOut, UserOut
from app.security import create_token, hash_password, verify_password
from app.services.booking import ID_LOCK, next_id

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Verifying against a fixed hash keeps unknown-email timing close to wrong-password.
_DUMMY_HASH = hash_password("not-a-real-password")


def _user_out(user: CurrentUser) -> UserOut:
    return UserOut(
        user_id=user.user_id,
        email=user.email,
        roles=sorted(user.roles),
        guest_id=user.guest_id,
        full_name=user.full_name,
    )


def _secret(request: Request) -> str:
    secret = request.app.state.settings.auth_secret
    if not secret:
        raise ApiError(
            503, "AUTH_NOT_CONFIGURED", "Máy chủ chưa cấu hình AUTH_SECRET để đăng nhập."
        )
    return secret


@router.post("/register", response_model=UserOut, status_code=201, summary="Đăng ký tài khoản khách")
def register(body: RegisterRequest, request: Request) -> UserOut:
    email = body.email.lower()
    password_hash = hash_password(body.password)
    with get_tx(request) as connection:
        connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
        exists = connection.execute(
            "SELECT 1 FROM app_user WHERE lower(email) = %s", (email,)
        ).fetchone()
        if exists:
            raise conflict("EMAIL_TAKEN", "Email này đã được đăng ký.")
        role = connection.execute("SELECT role_id FROM role WHERE code = 'GUEST'").fetchone()
        if role is None:
            raise ApiError(503, "ROLE_MISSING", "Hệ thống chưa có vai trò GUEST.")
        user_id = next_id(connection, "app_user", "user_id")
        guest_id = next_id(connection, "guest", "guest_id")
        connection.execute(
            "INSERT INTO app_user (user_id, email, password_hash, is_active, created_at) "
            "VALUES (%s, %s, %s, TRUE, now())",
            (user_id, email, password_hash),
        )
        connection.execute(
            "INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)",
            (user_id, role["role_id"]),
        )
        connection.execute(
            "INSERT INTO guest (guest_id, user_id, full_name, phone, email) "
            "VALUES (%s, %s, %s, %s, %s)",
            (guest_id, user_id, body.full_name.strip(), body.phone, email),
        )
        user = load_user(connection, user_id)
    return _user_out(user)


@router.post("/login", response_model=TokenOut, summary="Đăng nhập, nhận access token")
def login(body: LoginRequest, request: Request) -> TokenOut:
    secret = _secret(request)
    with get_db(request) as connection:
        row = connection.execute(
            "SELECT user_id, password_hash FROM app_user "
            "WHERE lower(email) = %s ORDER BY user_id LIMIT 1",
            (body.email.lower(),),
        ).fetchone()
        stored = row["password_hash"] if row else _DUMMY_HASH
        valid = verify_password(body.password, stored) and row is not None
        user = load_user(connection, row["user_id"]) if valid else None
    if user is None:
        raise unauthorized("Email hoặc mật khẩu không đúng.")
    ttl = request.app.state.settings.token_ttl_seconds
    return TokenOut(
        access_token=create_token(user.user_id, secret, ttl),
        expires_in=ttl,
        user=_user_out(user),
    )


@router.get("/me", response_model=UserOut, summary="Thông tin tài khoản đang đăng nhập")
def me(user: CurrentUser = Depends(current_user)) -> UserOut:
    return _user_out(user)
