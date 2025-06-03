from sqlalchemy import Column, Integer, String, Text, Numeric, SmallInteger
from sqlalchemy.orm import validates

from app.core.base_model import BaseEntity

class Wishlist(BaseEntity):
    
    __tablename__ = 'wishlist'
    
    product_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary with status properly serialized"""
        result = super().to_dict()
        # Ensure status is serialized as a string value
        result['status'] = self.status.value if self.status else None
        return result