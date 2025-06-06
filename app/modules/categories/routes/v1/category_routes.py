from fastapi import APIRouter, Depends
from app.core.base_model import APIResponse
from app.enums.base_enums import BaseErrorCode
from app.exceptions.handlers import handle_exceptions
from app.middleware.translation_manager import _
from app.modules.categories.repository.category_repo import CategoryRepo

route = APIRouter(prefix='/categories', tags=['Categories'])

@route.get('/', response_model=APIResponse)
@handle_exceptions
async def get_all_categories(
    repo: CategoryRepo = Depends(),
):
    """Get all categories with their IDs and names"""
    categories = repo.get_all_categories()
    return APIResponse(
        error_code=BaseErrorCode.ERROR_CODE_SUCCESS,
        message=_('operation_successful'),
        data=categories,
    )