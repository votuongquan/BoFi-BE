from pydantic import ConfigDict, Field
from app.core.base_model import ResponseSchema
from typing import List

class CategoryResponse(ResponseSchema):
    """Response schema for a single category"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description='Category ID',
        examples=[1, 2, 3],
    )
    name_category: str = Field(
        ...,
        description='Category name',
        examples=['Clothing', 'Electronics', 'Accessories'],
    )