from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    This also acts as the sync point for frontend to provision a new user 
    if they just registered via Firebase.
    """
    return current_user

@router.post("/sync", response_model=User)
def sync_user_profile(current_user: User = Depends(get_current_user)):
    """
    Explicitly sync/provision user after frontend registration.
    """
    return current_user
