from sqlalchemy import Column, Integer, Enum, DateTime, Numeric, String
from sqlalchemy.orm import validates

from app.core.base_model import BaseEntity

class Size(BaseEntity):
    
    __tablename__ = 'sizes'
    
    size_name = Column(String(50), nullable=False, unique=True)
    
    @validates('size_name')
    def validate_size_name(self, key, size_name):
        if not size_name or len(size_name) < 1:
            raise ValueError('Size name must be at least 1 character long')
        return size_name

    def to_dict(self):
        """Convert model to dictionary"""
        result = super().to_dict()
        return result