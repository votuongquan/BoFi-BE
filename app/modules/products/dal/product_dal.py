import logging
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.core.base_dal import BaseDAL
from app.core.base_model import Pagination
from app.enums.base_enums import Constants
from app.modules.products.models.products import Product

logger = logging.getLogger(__name__)

class ProductDAL(BaseDAL[Product]):
    """Data Access Layer for Product model"""

    def __init__(self, db: Session):
        super().__init__(db, Product)

    def get_product_by_id(self, product_id: int) -> Product:
        """Get a product by its ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def search_products(self, params: dict) -> Pagination[Product]:
        """Search products with pagination, filtering, and sorting"""
        logger.info(f'Searching products with parameters: {params}')
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', Constants.PAGE_SIZE))
        price = params.get('price')
        sort_by = params.get('sort_by')
        sort_order = params.get('sort_order', 'asc')

        # Start with basic query
        query = self.db.query(Product)

        # Apply filters
        if price is not None:
            query = query.filter(Product.price == price)

        # Apply sorting
        if sort_by and hasattr(Product, sort_by):
            sort_column = getattr(Product, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            if sort_by:
                logger.warning(f"Invalid sort_by field: {sort_by}")

        # Count total records
        total_count = query.count()

        # Apply pagination
        products = query.offset((page - 1) * page_size).limit(page_size).all()

        logger.info(f'Found {total_count} products, returning page {page} with {len(products)} items')

        return Pagination(
            items=products,
            total_count=total_count,
            page=page,
            page_size=page_size
        )