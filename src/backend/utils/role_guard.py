"""
Centralized Role-Based Access Control (RBAC) Dependency.
"""

from typing import Iterable

from fastapi import Depends, HTTPException, status

from backend.api.deps import get_current_user
from backend.models.user import User, UserRole


class RoleGuard:
    """
    Dependency class for enforcing role-based access.

    Usage:
        Depends(RoleGuard([UserRole.TEACHER]))
        Depends(RoleGuard([UserRole.STUDENT, UserRole.TEACHER]))
    """

    def __init__(self, allowed_roles: Iterable[UserRole]):
        self.allowed_roles = set(allowed_roles)

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user