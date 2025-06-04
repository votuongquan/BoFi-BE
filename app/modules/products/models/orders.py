from sqlalchemy import Column, Integer, Enum, DateTime, Numeric, String
from sqlalchemy.orm import validates, relationship

from app.core.base_model import BaseEntity

class Order(BaseEntity):
    """Order model"""

    __tablename__ = 'orders'

    product_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    # Assuming status is a string enum
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False,
                        server_default="CURRENT_TIMESTAMP")

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError('Quantity must be greater than 0')
        return quantity

    @validates('total_price')
    def validate_total_price(self, key, total_price):
        if total_price <= 0:
            raise ValueError('Total price must be greater than 0')
        return total_price

    def to_dict(self):
        """Convert model to dictionary with status properly serialized"""
        result = super().to_dict()
        # Ensure status is serialized as a string value
        result['status'] = self.status.value if self.status else None
        return result