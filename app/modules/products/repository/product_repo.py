import logging
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.base_model import Pagination
from app.core.base_repo import BaseRepo
from app.core.database import get_db
from app.exceptions.exception import NotFoundException
from app.middleware.translation_manager import _
from app.modules.products.dal.product_dal import ProductDAL
from app.modules.products.schemas.product_request import SearchProductRequest
from app.modules.products.models.products import Product
from app.modules.products.models.orders import Order
from app.modules.products.models.wishlists import Wishlist
from app.modules.products.schemas.product_response import ProductResponse
from sqlalchemy import and_

logger = logging.getLogger(__name__)

class ProductRepo(BaseRepo):
    """Repository for product-related operations"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.product_dal = ProductDAL(db)

    # File: product_repo.py

    def get_product_by_id(self, product_id: int):  # Change return type to ProductResponse
        """Retrieve a product by its ID"""
        product = self.product_dal.get_product_by_id(product_id)
        if not product:
            raise NotFoundException(_('product_not_found'))
        
        # Fetch sizes for the product
        sizes = self.product_dal.get_product_sizes(product_id)
        
        # Convert product to ProductResponse and include sizes
        product_response = ProductResponse.model_validate(product)
        product_response.size = sizes  # Assign sizes to the response
        return product_response

    # File: product_repo.py

    def search_products(self, request: SearchProductRequest) -> Pagination[ProductResponse]:
        """Search products with pagination, filtering, and sorting"""
        try:
            # Get the paginated products from ProductDAL
            result = self.product_dal.search_products(request.model_dump())
            
            # Fetch sizes for all products in one query
            product_ids = [product.id for product in result.items]
            size_map = self.product_dal.get_product_sizes_batch(product_ids)
            
            # Create ProductResponse objects
            product_responses = []
            for product in result.items:
                product_response = ProductResponse.model_validate(product)
                product_response.size = size_map.get(product.id, [])
                product_responses.append(product_response)
            
            # Return updated Pagination
            return Pagination(
                items=product_responses,
                total_count=result.total_count,
                page=result.page,
                page_size=result.page_size
            )
        except Exception as ex:
            logger.exception(f"Error searching products: {ex}")
            raise

    def get_shopping_history(self, user_id: int, page: int = 1, page_size: int = 10) -> Pagination:
        """Retrieve shopping history for a user with completed orders"""
        try:
            query = self.db.query(
                Product.name,
                Product.price,
                Product.main_image_url,
                Order.quantity,
                Order.total_price,
                Order.created_at
            ).join(
                Order, Product.id == Order.product_id
            ).filter(
                and_(
                    Order.user_id == user_id,
                    Order.status == "completed"
                )
            )

            # Count total records
            total_count = query.count()

            # Apply pagination
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            # Convert query results to dict for response
            history_items = [
                {
                    "name": item[0],
                    "price": float(item[1]),
                    "main_image_url": item[2],
                    "quantity": item[3],
                    "total_price": float(item[4]),
                    "created_at": item[5]
                } for item in items
            ]

            logger.info(f"Found {total_count} completed orders for user {user_id}, returning page {page} with {len(history_items)} items")

            return Pagination(
                items=history_items,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
        except Exception as ex:
            logger.exception(f"Error retrieving shopping history: {ex}")
            raise

    def get_wishlist(self, user_id: int, page: int = 1, page_size: int = 10) -> Pagination:
        """Retrieve wishlist for a user"""
        try:
            query = self.db.query(
                Product.name,
                Product.price,
                Product.main_image_url
            ).join(
                Wishlist, Product.id == Wishlist.product_id
            ).filter(
                Wishlist.user_id == user_id
            )

            # Count total records
            total_count = query.count()

            # Apply pagination
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            # Convert query results to dict for response
            wishlist_items = [
                {
                    "name": item[0],
                    "price": float(item[1]),
                    "main_image_url": item[2]
                } for item in items
            ]

            logger.info(f"Found {total_count} wishlist items for user {user_id}, returning page {page} with {len(wishlist_items)} items")

            return Pagination(
                items=wishlist_items,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
        except Exception as ex:
            logger.exception(f"Error retrieving wishlist: {ex}")
            raise