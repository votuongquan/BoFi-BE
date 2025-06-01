"""
Authentication API Routes for Google OAuth

This module handles Google OAuth authentication endpoints
"""

import requests
from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.base_model import APIResponse
from app.core.config import FRONTEND_ERROR_URL, FRONTEND_SUCCESS_URL
from app.enums.base_enums import BaseErrorCode
from app.exceptions.exception import CustomHTTPException
from app.exceptions.handlers import handle_exceptions
from app.http.oauth2 import get_current_user
from app.middleware.translation_manager import _
from app.modules.users.repository.authen_repo import AuthenRepo
from app.modules.users.schemas.users import (
	UserResponse,
    LoginRequest,
	SignupRequest
)

import logging

route = APIRouter(prefix='/auth', tags=['Authentication'])
logger = logging.getLogger(__name__)

@route.post('/login', response_model=APIResponse)
@handle_exceptions
async def login(credentials: LoginRequest, repo: AuthenRepo = Depends()) -> APIResponse:
    """Login endpoint: Validate credentials and return tokens"""
    result = repo.login(credentials)
    print('Login result:', result)
    response = UserResponse.model_validate(result)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('login_success'),
        data=response,
    )

@route.post('/signup', response_model=APIResponse)
@handle_exceptions
async def signup(user: SignupRequest, repo: AuthenRepo = Depends()) -> APIResponse:
    """Signup endpoint: Register a new user"""
    result = await repo.signup(user)
    response = UserResponse.model_validate(result)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('signup_success'),
        data=response,
    )
