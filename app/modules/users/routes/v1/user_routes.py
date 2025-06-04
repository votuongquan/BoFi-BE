import json

from fastapi import APIRouter, Depends, Query, Body
from app.modules.products.repository.product_repo import ProductRepo
from app.modules.products.schemas.product_request import SearchProductRequest, SortOrder
from app.modules.products.schemas.product_response import ProductResponse, ShoppingHistoryResponse, ShoppingHistoryItem, WishlistResponse, WishlistItem

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

route = APIRouter(
    prefix='/users', tags=['Users'], dependencies=[Depends(verify_token)])


@route.get('/info', response_model=APIResponse)
@handle_exceptions
async def get_current_user_profile(current_user_payload: dict = Depends(get_current_user), repo: UserRepo = Depends()):
    """
    Get the profile of the currently authenticated user

    This endpoint returns the full profile information of the authenticated user
    based on their access token.
    """
    user_id = current_user_payload.get('user_id')
    user = repo.get_user_by_id(user_id)

    if not user:
        raise CustomHTTPException(message=_('user_not_found'))

    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=UserResponse.model_validate(user),
    )


@route.get('/history', response_model=APIResponse)
@handle_exceptions
async def get_shopping_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get shopping history for a user with completed orders"""

    user_id = current_user_payload.get('user_id')
    result = repo.get_shopping_history(user_id, page, page_size)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=PaginatedResponse[ShoppingHistoryItem](
            items=[ShoppingHistoryItem.model_validate(
                item) for item in result.items],
            paging=PagingInfo(
                total=result.total_count,
                total_pages=result.total_pages,
                page=result.page,
                page_size=result.page_size,
            ),
        ),
    )


@route.get('/wishlist', response_model=APIResponse)
@handle_exceptions
async def get_wishlist(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get wishlist for a user"""

    user_id = current_user_payload.get('user_id')
    result = repo.get_wishlist(user_id, page, page_size)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=PaginatedResponse[WishlistItem](
            items=[WishlistItem.model_validate(item) for item in result.items],
            paging=PagingInfo(
                total=result.total_count,
                total_pages=result.total_pages,
                page=result.page,
                page_size=result.page_size,
            ),
        ),
    )


@route.post('/wishlist', response_model=APIResponse)
@handle_exceptions
async def add_to_wishlist(
    product_id: int = Body(...,
                           description='ID of the product to add to wishlist'),
    current_user_payload: dict = Depends(get_current_user),
    repo: UserRepo = Depends(),
):
    """Add a product to the user's wishlist"""

    user_id = current_user_payload.get('user_id')
    result = repo.add_to_wishlist(user_id, product_id)

    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=WishlistItem.model_validate(result),
    )
