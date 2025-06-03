import json
from fastapi import APIRouter, Depends, Query
from app.core.base_model import APIResponse, PagingInfo
from app.enums.base_enums import BaseErrorCode
from app.exceptions.handlers import handle_exceptions
from app.middleware.translation_manager import _
from app.modules.products.repository.product_repo import ProductRepo
from app.modules.products.schemas.product_request import SearchProductRequest, SortOrder
from app.modules.products.schemas.product_response import ProductResponse, ShoppingHistoryResponse, ShoppingHistoryItem, WishlistResponse, WishlistItem
from app.http.oauth2 import get_current_user
from app.middleware.auth_middleware import verify_token
from app.core.base_model import ResponseSchema, APIResponse, PaginatedResponse

route = APIRouter(prefix='/products',
                  tags=['Products'], dependencies=[Depends(verify_token)])


@route.get('/', response_model=APIResponse)
@handle_exceptions
async def search_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    price: float | None = Query(None, description='Filter by price'),
    sort_by: str | None = Query(
        None, description='Field to sort by (e.g., price, name)'),
    sort_order: SortOrder = Query(
        SortOrder.ASC, description='Sort order: asc or desc'),
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get all products with pagination, filtering, and sorting

    Supports filtering by price via query parameters.
    Example:
    GET /products/?page=1&page_size=10&price=10.0&sort_by=price&sort_order=desc
    """
    request = SearchProductRequest(
        page=page,
        page_size=page_size,
        price=price,
        sort_by=sort_by,
        sort_order=sort_order
    )
    result = repo.search_products(request)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=PaginatedResponse[ProductResponse](
            items=[ProductResponse.model_validate(
                product) for product in result.items],
            pacing=PagingInfo(
                total=result.total_count,
                total_pages=result.total_pages,
                page=result.page,
                page_size=result.page_size,
            ),
        ),
    )


@route.get('/{product_id}', response_model=APIResponse)
@handle_exceptions
async def get_product_by_id(
    product_id: int,
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get a product by its ID"""
    product = repo.get_product_by_id(product_id)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=ProductResponse.model_validate(product),
    )


@route.get('/history/{user_id}', response_model=APIResponse)
@handle_exceptions
async def get_shopping_history(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get shopping history for a user with completed orders"""
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


@route.get('/wishlist/{user_id}', response_model=APIResponse)
@handle_exceptions
async def get_wishlist(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    current_user_payload: dict = Depends(get_current_user),
    repo: ProductRepo = Depends(),
):
    """Get wishlist for a user"""
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
