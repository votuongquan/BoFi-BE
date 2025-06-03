"""
User Request and Response Schemas for Google OAuth
"""

from datetime import datetime
from typing import List

from fastapi import Body
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.base_model import (
	APIResponse,
	FilterableRequestSchema,
	PaginatedResponse,
	RequestSchema,
	ResponseSchema,
)
from app.enums.user_enums import UserRoleEnum
from app.middleware.translation_manager import _

from app.exceptions.exception import (
	CustomHTTPException,
	ForbiddenException,
	NotFoundException,
	UnauthorizedException,
	ValidationException,
)

class UserResponse(ResponseSchema):
	"""User info Response model"""

	id: int = Field(
		...,
		description='User ID',
		examples=['d9fc5dc0-e4b7-4a7d-83a1-7dda5fed129b'],
	)
	username: str | None = Field(default=None, description='Username', examples=['johndoe'])
	password: str | None = Field(default=None, description='Password (hashed)', examples=['$2b$12$...'])
	email: str | None = Field(default=None, description='Email address', examples=['abc@gmail.com'])
	full_name: str | None = Field(default=None, description='Full name', examples=['John Doe'])
	phone: str | None = Field(default=None, description='Phone number', examples=['+1234567890'])
	address: str | None = Field(default=None, description='Address', examples=['123 Main St, City, Country'])
	avatar: str | None = Field(default=None, description='Avatar URL', examples=['https://example.com/avatar.jpg'])
	is_active: bool = Field(default=True, description='Account active status', examples=[True])
	role: UserRoleEnum = Field(
		default=UserRoleEnum.CUSTOMER,
		description='User role',
		examples=[UserRoleEnum.CUSTOMER, UserRoleEnum.ADMIN],
	)
	create_date: datetime | None = Field(default=None, description='Creation date', examples=['2024-09-01 15:00:00'])
	update_date: datetime | None = Field(default=None, description='Update date', examples=['2024-09-01 15:00:00'])

	access_token: str | None = Field(default=None, description='Access token', examples=['xaasvwewe'])
	refresh_token: str | None = Field(default=None, description='Refresh token', examples=['xaasvwewe'])
	token_type: str | None = Field(default=None, description='Token type', examples=['bearer'])
 
class LoginRequest(RequestSchema):
    """Login Request model"""

    username: str = Field(..., min_length=3, description='Tên đăng nhập')
    password: str = Field(..., description=_('password'))
 
class SignupRequest(RequestSchema):
    """SignupRequest"""

    email: EmailStr = Field(..., description='Địa chỉ email')
    username: str = Field(..., min_length=3, description='Tên đăng nhập')
    password: str = Field(..., min_length=6, description='Mật khẩu')
    full_name: str | None = Field(default=None, description='Họ và tên đầy đủ')
    role: UserRoleEnum | None = Field(default=UserRoleEnum.CUSTOMER, description='Quyền người dùng')

    @field_validator('password')
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValidationException(message=_('password_too_short'))
        elif len(password) > 20:
            raise ValidationException(message=_('password_too_long'))
        if not any(char.isdigit() for char in password):
            raise ValidationException(message=_('password_must_contain_digit'))
        if not any(char.isupper() for char in password):
            raise ValidationException(message=_('password_must_contain_uppercase'))
        if not any(char.islower() for char in password):
            raise ValidationException(message=_('password_must_contain_lowercase'))
        if not any(char in '!@#$%^&*()-_=+[]{};:,.<>?/' for char in password):
            raise ValidationException(message=_('password_must_contain_special_character'))
        return password


class SearchUserRequest(FilterableRequestSchema):
	"""SearchUserRequest - Provides dynamic search filters for users"""


class RefreshTokenRequest(RequestSchema):
	"""RefreshTokenRequest"""

	refresh_token: str = Field(..., description='Refresh token')


class SearchUserResponse(APIResponse):
	"""SearchUserResponse"""

	data: PaginatedResponse[UserResponse] | None


class OAuthUserInfo(BaseModel):
	"""OAuth user information model"""

	email: str
	name: str | None = None
	picture: str | None = None
	given_name: str | None = None
	family_name: str | None = None
	locale: str | None = None
	sub: str  # OAuth subject/user id
	granted_scopes: List[str] | None = None  # List of scopes granted by the user
