from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.auth.utils import get_current_active_user


def require_role(roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


def require_attendee(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ATTENDEE:
        raise HTTPException(status_code=403, detail="Only attendees can perform this action")
    return current_user


def require_organizer(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ORGANIZER:
        raise HTTPException(status_code=403, detail="Only organizers can perform this action")
    return current_user
