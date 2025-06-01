"""User role enums"""

from enum import Enum


class UserRoleEnum(str, Enum):
	"""User role enumeration"""

	ADMIN = 'admin'
	CUSTOMER = 'customer'
