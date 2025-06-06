import logging
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.core.base_dal import BaseDAL
from app.core.base_model import Pagination
from app.enums.base_enums import Constants
from app.modules.products.models.products import Product
from app.modules.products.models.size_product import SizeProduct
from app.modules.products.models.sizes import Size

logger = logging.getLogger(__name__)

class ProductDAL(BaseDAL[Product]):
    """Data Access Layer for Product model"""

    def __init__(self, db: Session):
        super().__init__(db, Product)

    def get_product_by_id(self, product_id: int) -> Product:
        """Get a product by its ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_sizes(self, product_id: int) -> list[str]:
        """Get all size names for a given product ID, sorted by XS, S, M, L, XL, XXL"""
        try:
            logger.info(f"Fetching sizes for product_id: {product_id}")
            size_names = (
                self.db.query(Size.size_name)
                .join(SizeProduct, Size.id == SizeProduct.size_id)
                .filter(SizeProduct.product_id == product_id)
                .all()
            )
            size_names = [size_name for (size_name,) in size_names]

            # Define custom sort order
            size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
            # Sort sizes according to the predefined order
            sorted_sizes = sorted(
                size_names,
                key=lambda x: size_order.index(
                    x) if x in size_order else len(size_order)
            )

            logger.info(
                f"Found {len(sorted_sizes)} sizes for product_id {product_id}: {sorted_sizes}")
            return sorted_sizes
        except Exception as ex:
            logger.exception(
                f"Error fetching sizes for product_id {product_id}: {ex}")
            raise

    def get_product_sizes_batch(self, product_ids: list[int]) -> dict[int, list[str]]:
        """Get size names for multiple product IDs, sorted by XS, S, M, L, XL, XXL"""
        try:
            logger.info(f"Fetching sizes for product_ids: {product_ids}")
            size_data = (
                self.db.query(Product.id, Size.size_name)
                .join(SizeProduct, SizeProduct.product_id == Product.id)
                .join(Size, Size.id == SizeProduct.size_id)
                .filter(Product.id.in_(product_ids))
                .all()
            )

            # Group sizes by product_id
            size_map = {}
            for product_id, size_name in size_data:
                if product_id not in size_map:
                    size_map[product_id] = []
                size_map[product_id].append(size_name)

            # Sort sizes according to the predefined order
            size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
            for product_id in size_map:
                size_map[product_id] = sorted(
                    size_map[product_id],
                    key=lambda x: size_order.index(x) if x in size_order else len(size_order)
                )

            logger.info(f"Found sizes for {len(size_map)} products")
            return size_map
        except Exception as ex:
            logger.exception(f"Error fetching sizes for product_ids {product_ids}: {ex}")
            raise

    def search_products(self, params: dict) -> Pagination[Product]:
        """Search products with pagination, filtering, and sorting"""
        logger.info(f'Searching products with parameters: {params}')
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', Constants.PAGE_SIZE))
        item_type = params.get('item_type')
        size_type = params.get('size_type')
        sort_by = params.get('sort_by')
        sort_order = params.get('sort_order', 'asc')

        # Start with basic query
        query = self.db.query(Product)

        # Apply filters
        if item_type is not None:
            logger.info(f"Filtering products by item_type: {item_type}")
            query = query.filter(Product.category_id == item_type)

        if size_type is not None:
            logger.info(f"Filtering products by size_type: {size_type}")
            query = (
                query.join(SizeProduct, Product.id == SizeProduct.product_id)
                     .join(Size, Size.id == SizeProduct.size_id)
                     .filter(Size.size_name == size_type)
            )

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

        logger.info(
            f'Found {total_count} products, returning page {page} with {len(products)} items')

        return Pagination(
            items=products,
            total_count=total_count,
            page=page,
            page_size=page_size
        )