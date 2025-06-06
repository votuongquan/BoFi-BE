import json
from fastapi import APIRouter, Depends, Query
from app.core.base_model import APIResponse, PagingInfo
from app.enums.base_enums import BaseErrorCode
from app.exceptions.handlers import handle_exceptions
from app.middleware.translation_manager import _
from app.modules.products.repository.product_repo import ProductRepo
from app.modules.products.schemas.product_request import SearchProductRequest, SortOrder
from app.modules.products.schemas.product_response import ProductResponse, ShoppingHistoryResponse, ShoppingHistoryItem, WishlistResponse, WishlistItem
from app.core.base_model import APIResponse, PaginatedResponse

route = APIRouter(prefix='/products',
                  tags=['Products'])

@route.get('/', response_model=APIResponse)
@handle_exceptions
async def search_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    item_type: int | None = Query(None, description='Filter by type'),
    size_type: str | None = Query(
        None, description='Filter by size (e.g., S, M, L)'),
    sort_by: str | None = Query(
        None, description='Field to sort by (e.g., price, name)'),
    sort_order: SortOrder = Query(
        SortOrder.ASC, description='Sort order: asc or desc'),
    repo: ProductRepo = Depends(),
):
    """Get all products with pagination, filtering, and sorting

    Supports filtering by item_type and size_type via query parameters.
    Example:
    GET /products/?page=1&page_size=10&item_type=10&sort_by=price&sort_order=desc&size_type=S
    """
    request = SearchProductRequest(
        page=page,
        page_size=page_size,
        item_type=item_type,
        size_type=size_type,
        sort_by=sort_by,
        sort_order=sort_order
    )
    result = repo.search_products(request)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=PaginatedResponse[ProductResponse](
            items=result.items,
            paging=PagingInfo(
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
    repo: ProductRepo = Depends(),
):
    """Get a product by its ID"""
    product_response = repo.get_product_by_id(product_id)
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=product_response,
    )