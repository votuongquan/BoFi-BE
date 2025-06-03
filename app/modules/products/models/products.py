
from sqlalchemy import Column, Integer, String, Text, Numeric, SmallInteger
from sqlalchemy.orm import validates

from app.core.base_model import BaseEntity


class Product(BaseEntity):
    """Product model"""

    __tablename__ = 'products'

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    brand_id = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    main_image_url = Column(String(255), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, nullable=False)
    collab_status = Column(SmallInteger, nullable=False, default=0)

    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name) < 3:
            raise ValueError('Product name must be at least 3 characters long')
        return name

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError('Price must be greater than 0')
        return price

    @validates('stock')
    def validate_stock(self, key, stock):
        if stock < 0:
            raise ValueError('Stock cannot be negative')
        return stock

    def to_dict(self):
        """Convert model to dictionary"""
        result = super().to_dict()
        return result