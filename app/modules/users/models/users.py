"""User model"""

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import validates

from app.core.base_model import BaseEntity
from app.enums.user_enums import UserRoleEnum


class User(BaseEntity):
	"""User model"""

	__tablename__ = 'users'
	
	username = Column(String(255), nullable=True)
	password = Column(String(255), nullable=True)
	email = Column(String(255), nullable=True)
	full_name = Column(String(255), nullable=True)
	phone = Column(String(255), nullable=True)
	address = Column(String(255), nullable=True)
	avatar = Column(String(255), nullable=True)
	is_active = Column(Boolean, nullable=False, default=True)
	role = Column(String(50), nullable=False, default="customer")

	@validates('email')
	def validate_email(self, key, address):
		if address and '@' not in address:
			raise ValueError('Invalid email address')
		return address

	@validates('username')
	def validate_username(self, key, username):
		if username and len(username) < 3:
			raise ValueError('Username must be at least 3 characters long')
		return username

	def to_dict(self):
		"""Convert model to dictionary with role properly serialized"""
		result = super().to_dict()
		# Ensure role is serialized as a string value
		return result