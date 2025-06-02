from typing import Optional
from pydantic import ConfigDict
from app.core.base_model import RequestSchema
from enum import Enum

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SearchProductRequest(RequestSchema):
    """Request schema for searching products with pagination, filters, and sorting"""
    model_config = ConfigDict(from_attributes=True)

    page: int = 1
    page_size: int = 10
    price: Optional[float] = None
    sort_by: Optional[str] = None
    sort_order: Optional[SortOrder] = SortOrder.ASC