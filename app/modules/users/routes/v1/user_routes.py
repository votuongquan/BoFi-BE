import json

from fastapi import APIRouter, Depends, Query

from app.core.base_model import APIResponse, PagingInfo
from app.enums.base_enums import BaseErrorCode
from app.exceptions.exception import CustomHTTPException, NotFoundException
from app.exceptions.handlers import handle_exceptions
from app.http.oauth2 import get_current_user
from app.middleware.auth_middleware import verify_token
from app.middleware.translation_manager import _
from app.modules.users.repository.user_repo import UserRepo
from app.modules.users.schemas.users import (
	PaginatedResponse,
	SearchUserRequest,
	SearchUserResponse,
	UserResponse,
)

route = APIRouter(prefix='/users', tags=['Users'], dependencies=[Depends(verify_token)])

@route.get('/{user_id}', response_model=APIResponse)
@handle_exceptions
async def get_user_by_id(
	user_id: int,
	current_user_payload: dict = Depends(get_current_user),
	repo: UserRepo = Depends(),
):
	"""
	Get user information by ID

	Args:
		user_id: The ID of the user to retrieve

	Returns:
		APIResponse with UserResponse containing user information (id, username, email, full_name, phone, address, is_active, avatar, role)
	"""
	user = repo.get_user_by_id(user_id)
	if not user:
		raise NotFoundException(_('user_not_found'))
	return APIResponse(
		error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
		message=_('operation_successful'),
		data=UserResponse.model_validate(user),
	)