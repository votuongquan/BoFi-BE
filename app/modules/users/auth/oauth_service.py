"""OAuth service for handling Google authentication"""

import logging
from datetime import datetime

from pytz import timezone

from app.exceptions.exception import CustomHTTPException
from app.enums.user_enums import UserRoleEnum
from app.middleware.translation_manager import _
from app.modules.users.models.users import User
from app.modules.users.schemas.users import OAuthUserInfo, RefreshTokenRequest
from app.modules.users.auth.auth_utils import generate_auth_tokens, verify_refresh_token
from app.core.events import EventHooks

logger = logging.getLogger(__name__)


class OAuthService:
	"""Service for handling Google OAuth authentication"""

	def __init__(self, user_dal, db):
		"""Initialize the OAuth service

		Args:
		    user_dal: User data access layer
		    db: Database session
		"""
		self.user_dal = user_dal
		self.db = db

	async def login_with_google(self, user_info: OAuthUserInfo):
		"""Login or register a user with Google OAuth

		Args:
		    user_info (OAuthUserInfo): Google user information

		Returns:
		    dict: User information with tokens including is_new_user flag

		Raises:
		    CustomHTTPException: If login fails
		"""
		try:
			# Track if this is a new user registration
			is_new_user = False

			# Look for existing user by Google ID
			user = self.user_dal.get_user_by_google_id(user_info.sub)

			# If no user found by Google ID, try email
			if not user:
				user = self.user_dal.get_user_by_email(user_info.email)
				if user:
					# Link existing account to Google
					update_data = {
						'google_id': user_info.sub,
						'profile_picture': user_info.picture,
						'first_name': user_info.given_name,
						'last_name': user_info.family_name,
						'name': user_info.name,
						'locale': user_info.locale,
						'update_date': datetime.now(timezone('Asia/Ho_Chi_Minh')),
					}
					user = self.user_dal.update(user.id, update_data)
				else:
					# Create a new user
					username = user_info.email.split('@')[0]
					if user_info.name:
						# Remove spaces and special chars for username
						username = ''.join(e for e in user_info.name if e.isalnum())

					new_user = {
						'email': user_info.email,
						'username': username,
						'role': UserRoleEnum.USER,
						'confirmed': True,  # Auto-confirm Google users
						'google_id': user_info.sub,
						'profile_picture': user_info.picture,
						'first_name': user_info.given_name,
						'last_name': user_info.family_name,
						'name': user_info.name,
						'locale': user_info.locale,
					}

					# Create new user in the database
					with self.user_dal.transaction():
						user = self.user_dal.create(new_user)
						self.db.flush()  # Ensure the user ID is generated

					is_new_user = True
			else:
				# Update existing user's profile with latest Google info
				update_data = {
					'profile_picture': user_info.picture,
					'update_date': datetime.now(timezone('Asia/Ho_Chi_Minh')),
				}
				user = self.user_dal.update(user.id, update_data)

			# Update last login timestamp
			user.last_login_at = datetime.now(timezone('Asia/Ho_Chi_Minh'))
			self.db.commit()

			# Generate tokens
			tokens = generate_auth_tokens(user)

			# Prepare response with tokens
			user_dict = user.to_dict()
			user_dict.update(tokens)
			user_dict['is_new_user'] = is_new_user

			# Log the successful OAuth login
			action = 'google_signup' if is_new_user else 'google_login'
			message = 'User signed up with Google' if is_new_user else 'User logged in with Google'

			# Trigger user_created event for new users only
			if is_new_user:
				try:
					event_hooks = EventHooks()
					event_hooks.trigger(
						'user_created',
						user_id=str(user.id),
						email=user.email,
						username=user.username
					)
					logger.info(f"Triggered user_created event for new user {user.id}")
				except Exception as e:
					logger.error(f"Failed to trigger user_created event for user {user.id}: {e}")
					# Don't let event system failure affect user creation

			return user_dict

		except Exception as ex:
			logger.error(f'Google login error: {ex}')
			raise CustomHTTPException(
				message=_('google_login_failed'),
			)

	async def refresh_token(self, request: RefreshTokenRequest):
		"""Refresh authentication tokens using a valid refresh token

		Args:
		    request (RefreshTokenRequest): Request with refresh token

		Returns:
		    dict: User info with new authentication tokens

		Raises:
		    CustomHTTPException: If token refresh fails
		"""
		try:
			# Verify and decode the refresh token
			claims = verify_refresh_token(request.refresh_token)

			# Get user from claims
			user: User = self.user_dal.get_by_id(claims['user_id'])
			if not user:
				raise CustomHTTPException(message=_('user_not_found'))

			# Generate new tokens
			tokens = generate_auth_tokens(user)

			# Prepare response with user data and new tokens
			user_dict = user.to_dict()
			user_dict.update(tokens)

			return user_dict

		except Exception as ex:
			if not isinstance(ex, CustomHTTPException):
				raise CustomHTTPException(
					message=_('invalid_refresh_token'),
				)
			raise ex
