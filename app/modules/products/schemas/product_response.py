from typing import List
from pydantic import ConfigDict
from app.core.base_model import ResponseSchema, APIResponse, PaginatedResponse
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class ProductResponse(ResponseSchema):
    """Response schema for a single product"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description='Product ID',
        examples=[1, 123, 4567],
    )
    name: str = Field(
        ...,
        description='Product name',
        examples=['iPhone 15 Pro', 'Nike Air Max', 'Samsung Galaxy S24'],
    )
    description: str | None = Field(
        default=None,
        description='Product description',
        examples=['Latest flagship smartphone with advanced camera system', None],
    )
    brand_id: int | None = Field(
        default=None,
        description='Brand ID reference',
        examples=[1, 25, 100, None],
    )
    price: float = Field(
        ...,
        description='Product price',
        examples=[999.99, 129.50, 25.00],
    )
    main_image_url: str | None = Field(
        default=None,
        description='Main product image URL',
        examples=['https://example.com/products/iphone15.jpg', None],
    )
    stock: int = Field(
        ...,
        description='Stock quantity',
        examples=[100, 0, 25],
    )
    category_id: int | None = Field(
        default=None,
        description='Category ID reference',
        examples=[1, 15, 42, None],
    )
    collab_status: int = Field(
        ...,
        description='Collaboration status',
        examples=[0, 1, 2],
    )
    size: List[str] = Field(
        default=[],
        description='List of size names for the product',
        examples=[['XS', 'S', 'M'], ['M', 'L', 'XL'], []],
    )
    create_date: datetime | None = Field(
        default=None, description='Creation date', examples=['2024-09-01 15:00:00'])
    update_date: datetime | None = Field(
        default=None, description='Update date', examples=['2024-09-01 15:00:00'])


class ShoppingHistoryItem(ResponseSchema):
    """Response schema for a single shopping history item"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        description='Product name',
        examples=['iPhone 15 Pro', 'Nike Air Max', 'Samsung Galaxy S24'],
    )
    price: float = Field(
        ...,
        description='Product price',
        examples=[999.99, 129.50, 25.00],
    )
    main_image_url: str | None = Field(
        default=None,
        description='Main product image URL',
        examples=['https://example.com/products/iphone15.jpg', None],
    )
    quantity: int = Field(
        ...,
        description='Ordered quantity',
        examples=[1, 2, 5],
    )
    total_price: float = Field(
        ...,
        description='Total price for the order',
        examples=[999.99, 259.00, 125.00],
    )
    created_at: datetime = Field(
        ...,
        description='Order creation date',
        examples=['2024-09-01 15:00:00'],
    )


class WishlistItem(ResponseSchema):
    """Response schema for a single wishlist item"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        description='Product name',
        examples=['iPhone 15 Pro', 'Nike Air Max', 'Samsung Galaxy S24'],
    )
    price: float = Field(
        ...,
        description='Product price',
        examples=[999.99, 129.50, 25.00],
    )
    main_image_url: str | None = Field(
        default=None,
        description='Main product image URL',
        examples=['https://example.com/products/iphone15.jpg', None],
    )


class ShoppingHistoryResponse(APIResponse):
    """Response schema for shopping history"""
    data: PaginatedResponse[ShoppingHistoryItem]


class WishlistResponse(APIResponse):
    """Response schema for wishlist"""
    data: PaginatedResponse[WishlistItem]
