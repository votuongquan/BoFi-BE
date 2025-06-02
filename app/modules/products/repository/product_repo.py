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

logger = logging.getLogger(__name__)

class ProductRepo(BaseRepo):
    """Repository for product-related operations"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.product_dal = ProductDAL(db)

    def get_product_by_id(self, product_id: int) -> Product:
        """Retrieve a product by its ID"""
        product = self.product_dal.get_product_by_id(product_id)
        if not product:
            raise NotFoundException(_('product_not_found'))
        return product

    def search_products(self, request: SearchProductRequest) -> Pagination[Product]:
        """Search products with pagination, filtering, and sorting"""
        try:
            return self.product_dal.search_products(request.model_dump())
        except Exception as ex:
            logger.exception(f"Error searching products: {ex}")
            raise