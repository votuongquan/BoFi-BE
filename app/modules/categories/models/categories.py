from sqlalchemy import Column, Integer, Enum, DateTime, Numeric, String
from sqlalchemy.orm import validates, relationship

from app.core.base_model import BaseEntity


class Category(BaseEntity):
    """Category model"""

    __tablename__ = 'categories'

    name_category = Column(String(100), nullable=False, unique=True)

    @validates('name_category')
    def validate_name_category(self, key, name_category):
        if not name_category:
            raise ValueError('Category name cannot be empty')
        return name_category

    def to_dict(self):
        """Convert model to dictionary"""
        result = super().to_dict()
        return result
