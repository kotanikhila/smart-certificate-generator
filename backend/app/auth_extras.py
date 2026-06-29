# Add to app/models.py
class UserType(str, enum.Enum):
    FOUNDATION = "foundation"
    NORMAL = "normal"
    ADMIN = "admin"  # NEW

# Add to app/auth.py
def require_admin(current_user: models.User = Depends(get_current_active_user)):
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
