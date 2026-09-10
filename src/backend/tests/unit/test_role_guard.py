from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.models.user import UserRole
from backend.utils.role_guard import RoleGuard


def _user(role):
    return SimpleNamespace(role=role)


async def test_allows_user_with_permitted_role():
    guard = RoleGuard([UserRole.TEACHER])
    user = _user(UserRole.TEACHER)
    result = await guard(current_user=user)
    assert result is user


async def test_rejects_user_without_permitted_role():
    guard = RoleGuard([UserRole.TEACHER])
    with pytest.raises(HTTPException) as exc_info:
        await guard(current_user=_user(UserRole.STUDENT))
    assert exc_info.value.status_code == 403


async def test_allows_any_of_multiple_permitted_roles():
    guard = RoleGuard([UserRole.TEACHER, UserRole.STUDENT])
    assert await guard(current_user=_user(UserRole.TEACHER)) is not None
    assert await guard(current_user=_user(UserRole.STUDENT)) is not None


async def test_empty_allowed_roles_rejects_everyone():
    guard = RoleGuard([])
    with pytest.raises(HTTPException) as exc_info:
        await guard(current_user=_user(UserRole.TEACHER))
    assert exc_info.value.status_code == 403


async def test_rejection_does_not_leak_which_roles_are_allowed():
    guard = RoleGuard([UserRole.TEACHER])
    with pytest.raises(HTTPException) as exc_info:
        await guard(current_user=_user(UserRole.STUDENT))
    assert "TEACHER" not in exc_info.value.detail
    assert "teacher" not in exc_info.value.detail.lower()
