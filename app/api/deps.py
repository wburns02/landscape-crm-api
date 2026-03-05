from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Header
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_maker
from app.exceptions import AuthError
from app.models.user import User


async def get_db():
    async with async_session_maker() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    access_token: str | None = Cookie(None),
    authorization: str | None = Header(None),
) -> User:
    token = None
    if access_token:
        token = access_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]

    if not token:
        raise AuthError("Not authenticated")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AuthError("Invalid token")
    except JWTError:
        raise AuthError("Invalid token")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalars().first()
    if not user:
        raise AuthError("User not found")
    if not user.is_active:
        raise AuthError("User is inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
