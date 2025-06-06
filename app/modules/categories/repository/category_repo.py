from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.categories.dal.category_dal import CategoryDAL
from app.modules.categories.schemas.category_response import CategoryResponse
import logging

logger = logging.getLogger(__name__)

class CategoryRepo:
    """Repository for category-related operations"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.category_dal = CategoryDAL(db)

    def get_all_categories(self) -> list[CategoryResponse]:
        """Retrieve all categories"""
        try:
            categories = self.category_dal.get_all_categories()
            category_responses = [CategoryResponse.model_validate(category) for category in categories]
            logger.info(f"Returning {len(category_responses)} categories")
            return category_responses
        except Exception as ex:
            logger.exception(f"Error retrieving categories: {ex}")
            raise