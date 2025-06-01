"""Authentication repository for Google OAuth"""

import logging
from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pytz import timezone

from app.core.base_repo import BaseRepo
from app.core.database import get_db
from app.modules.users.dal.user_dal import UserDAL
from app.middleware.translation_manager import _
from app.exceptions.exception import CustomHTTPException
from app.modules.users.auth.auth_utils import generate_auth_tokens, verify_refresh_token
from app.modules.users.schemas.users import OAuthUserInfo, RefreshTokenRequest, LoginRequest, SignupRequest
from app.modules.users.auth.oauth_service import OAuthService
from app.utils.password_utils import PasswordUtils
from app.enums.user_enums import UserRoleEnum

logger = logging.getLogger(__name__)


class AuthenRepo(BaseRepo):
    """Authentication repository for handling Google OAuth authentication

    This is the main entry point for Google OAuth authentication operations.
    """

    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the authentication repository

        Args:
            db (Session): Database session
        """
        self.db = db
        self.user_dal = UserDAL(db)

        # Initialize service
        self._oauth_service = None

    def get_oauth_service(self):
        """Get or initialize the OAuth service

        Returns:
            OAuthService: OAuth service instance
        """
        if not self._oauth_service:
            self._oauth_service = OAuthService(self.user_dal, self.db)
        return self._oauth_service

    def login(self, request: LoginRequest):
        """Handle user login with email and password

Args:
    request (LoginRequest): Login request with email and password

Returns:
    dict: User info with authentication tokens

Raises:
    NotFoundException: If user not found
    UnauthorizedException: If credentials are invalid
"""
        try:
            # Find user by email
            user = self.user_dal.get_user_by_email(request.email)
            if not user:
                raise CustomHTTPException(message=_('user_not_found'))

            # Verify password
            password_utils = PasswordUtils()
            if not password_utils.verify_password(request.password, user.password):
                raise UnauthorizedException(_('invalid_credentials'))

            # Update last login timestamp
            user.last_login_at = datetime.now(timezone('Asia/Ho_Chi_Minh'))
            self.db.commit()

            # Generate authentication tokens
            tokens = generate_auth_tokens(user)

            # Prepare response with user data and tokens
            user_dict = user.to_dict()
            user_dict.update(tokens)

            return user_dict

        except Exception as ex:
            raise ex

    async def signup(self, user: SignupRequest):
        """Register a new user

        Args:
                user (SignupRequest): User signup data

        Returns:
                dict: Created user information

        Raises:
                CustomHTTPException: If registration fails
        """
        try:
            # Check if user exists and is confirmed
            existing_user = self.user_dal.get_user_by_email(user.email)

            with self.user_dal.transaction():
                password_utils = PasswordUtils()
                hashed_password = password_utils.hash_password(user.password)

                new_user = {
                    'email': user.email,
                    'username': user.username,
                    'password': hashed_password,
                    'full_name': user.full_name,
                    'role': UserRoleEnum.CUSTOMER.value,  # Use enum value, not enum object
                }

                created_user = self.user_dal.create(new_user)
                self.db.commit()
                self.db.refresh(created_user)

                # Defensive: check if user was created
                if not created_user:
                    logger.error(
                        f"Signup failed: user creation returned None for email: {user.email}")
                    raise CustomHTTPException(message=_('signup_failed'))

                # Defensive: check if user is now in DB
                check_user = self.user_dal.get_user_by_email(user.email)
                if not check_user:
                    logger.error(
                        f"Signup failed: user not found after creation for email: {user.email}")
                    raise CustomHTTPException(message=_('signup_failed'))

                return created_user.to_dict()

        except CustomHTTPException as ex:
            # Already handled, just re-raise
            raise ex
        except Exception as ex:
            logger.exception(
                f"Unexpected error during signup for email {user.email}: {ex}")
            raise CustomHTTPException(message=_('signup_failed'))

    # ----- OAuth Methods -----
    async def refresh_token(self, request: RefreshTokenRequest):
        """Refresh user access token

        Args:
            request (RefreshTokenRequest): Request containing refresh token

        Returns:
            dict: New access token and user information
        """
        return await self.get_oauth_service().refresh_token(request)

    async def login_with_google(self, user_info: OAuthUserInfo):
        """Login or register a user with Google OAuth

        Args:
            user_info (OAuthUserInfo): Google user information

        Returns:
            dict: User information with tokens including is_new_user flag
        """
        return await self.get_oauth_service().login_with_google(user_info)

    async def log_oauth_token_revocation(self, user_id: str):
        """Log OAuth token revocation

        Args:
            user_id (str): The ID of the user revoking access

        Returns:
            bool: True if successful
        """
        return await self.get_oauth_service().log_oauth_token_revocation(user_id)
