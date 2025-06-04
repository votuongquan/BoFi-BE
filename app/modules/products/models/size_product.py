from sqlalchemy import Column, Integer, Enum, DateTime, Numeric, String
from sqlalchemy.orm import validates

from app.core.base_model import BaseEntity


class SizeProduct(BaseEntity):
    """SizeProduct model represents the association between products and sizes."""

    __tablename__ = 'size_product'

    product_id = Column(Integer, nullable=False)
    size_id = Column(Integer, nullable=False)

    @validates('product_id', 'size_id')
    def validate_ids(self, key, value):
        if value is None or value <= 0:
            raise ValueError(f'{key} must be a positive integer')
        return value

    def to_dict(self):
        """Convert model to dictionary"""
        result = super().to_dict()
        return result
