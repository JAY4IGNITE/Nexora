from typing import Optional
from app.core.supabase import supabase_client
from app.models.user import UserCreate, UserInDB
import logging

logger = logging.getLogger(__name__)

def get_user_by_firebase_uid(firebase_uid: str) -> Optional[UserInDB]:
    if not supabase_client:
        return None
    try:
        response = supabase_client.table("users").select("*").eq("firebase_uid", firebase_uid).execute()
        if response.data and len(response.data) > 0:
            return UserInDB(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error fetching user by UID: {e}")
        return None

def create_user(user_in: UserCreate) -> Optional[UserInDB]:
    if not supabase_client:
        return None
    try:
        data = user_in.model_dump()
        response = supabase_client.table("users").insert(data).execute()
        if response.data and len(response.data) > 0:
            return UserInDB(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None
