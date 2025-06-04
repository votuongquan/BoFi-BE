import json
import os
from functools import lru_cache

from dotenv import load_dotenv  # type: ignore
from pydantic import BaseModel

load_dotenv()
from urllib.parse import quote

PROJECT_NAME = 'CGSEM.AI'
API_V1_STR = '/api/v1'
API_V2_STR = '/api/v2'
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Tq14062004@')
DB_HOST = os.getenv('DB_HOST', 'localhost')

# Force host.docker.internal when running in Docker
# DB_HOST = 'host.docker.internal'

DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'bofitest3')
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

SQLALCHEMY_DATABASE_URI = DATABASE_URL

SERVICE = 'gemini'
MODEL_NAME = 'model/gemini-2.0-flash-exp'

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Google OAuth Settings

# Update the redirect URI to support Next.js frontend
GOOGLE_REDIRECT_URI = 'http://localhost:8000/api/v1/auth/google/callback'

# Frontend redirect URLs for OAuth flows - callback server on port 3000
FRONTEND_SUCCESS_URL = os.getenv('FRONTEND_SUCCESS_URL', 'http://127.0.0.1:5500/auth/google/callback')
FRONTEND_ERROR_URL = os.getenv('FRONTEND_ERROR_URL', 'http://127.0.0.1:5500/auth?error=true')

# JWT Settings
SECRET_KEY = os.getenv('SECRET_KEY', '-extremely-secret-and-very-long-key')
TOKEN_ISSUER = os.getenv('TOKEN_ISSUER', 'frecord-api')
TOKEN_AUDIENCE = os.getenv('TOKEN_AUDIENCE', 'frecord-client')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))


class Settings(BaseModel):
	PROJECT_NAME: str = PROJECT_NAME
	API_V1_STR: str = API_V1_STR
	API_V2_STR: str = API_V2_STR
	DATABASE_URL: str = DATABASE_URL
	SQLALCHEMY_DATABASE_URI: str = SQLALCHEMY_DATABASE_URI

	# JWT Settings
	SECRET_KEY: str = SECRET_KEY
	TOKEN_ISSUER: str = TOKEN_ISSUER
	TOKEN_AUDIENCE: str = TOKEN_AUDIENCE
	ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
	REFRESH_TOKEN_EXPIRE_DAYS: int = REFRESH_TOKEN_EXPIRE_DAYS


@lru_cache()
def get_settings():
	return Settings()
