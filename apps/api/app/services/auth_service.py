from sqlalchemy.orm import Session

from app.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.security.jwt import create_token, decode_token
from app.security.password import hash_password, needs_rehash, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        if self.users.get_by_email(payload.email):
            raise ConflictError("EMAIL_TAKEN", "An account with this email already exists")
        user = User(
            email=payload.email.lower(),
            name=payload.name,
            password_hash=hash_password(payload.password),
        )
        user = self.users.create(user)
        return self._tokens(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if user is None or not user.password_hash:
            raise UnauthorizedError("Invalid email or password")
        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(payload.password)
            self.users.save(user)
        return self._tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        user_id = decode_token(refresh_token, "refresh")
        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Invalid credentials")
        return self._tokens(user)

    def me(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def _tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_token(user.id, "access"),
            refresh_token=create_token(user.id, "refresh"),
        )
