from sqlalchemy.orm import Session
from app.core.base_dal import BaseDAL
from app.modules.categories.models.categories import Category
import logging

logger = logging.getLogger(__name__)

class CategoryDAL(BaseDAL[Category]):
    """Data Access Layer for Category model"""

    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_all_categories(self) -> list[Category]:
        """Retrieve all categories with id and name_category"""
        try:
            logger.info("Fetching all categories")
            categories = self.db.query(Category).all()
            
            # sort categories by id
            categories.sort(key=lambda x: x.id)
            
            logger.info(f"Found {len(categories)} categories")
            return categories
        except Exception as ex:
            logger.exception(f"Error fetching categories: {ex}")
            raise