import firebase_admin
from firebase_admin import credentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_firebase_app():
    if not firebase_admin._apps:
        if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CLIENT_EMAIL:
            # Handle encoded newlines from env vars
            private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": "dummy_key_id",
                "private_key": private_key,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": "dummy_client_id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
            })
            firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized successfully.")
        else:
            logger.warning("Firebase credentials missing. Using mock app for testing.")
            # For testing/mocking when no real credentials are provided
            try:
                cred = credentials.Certificate({"type": "service_account", "project_id": "test", "private_key": "test", "client_email": "test@test.com"})
            except:
                pass
            firebase_app = firebase_admin.initialize_app()
    else:
        firebase_app = firebase_admin.get_app()
    return firebase_app

# Initialize on import
firebase_app = get_firebase_app()
