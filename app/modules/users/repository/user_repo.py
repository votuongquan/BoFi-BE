"""User repo"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.base_model import Pagination
from app.core.base_repo import BaseRepo
from app.core.database import get_db
from app.exceptions.exception import CustomHTTPException, NotFoundException
from app.middleware.translation_manager import _
from app.modules.users.dal.user_dal import UserDAL
from app.modules.users.models.users import User
from app.modules.users.schemas.users import SearchUserRequest
from app.utils.password_utils import PasswordUtils
from fastapi import status

logger = logging.getLogger(__name__)


class UserRepo(BaseRepo):
	"""UserRepo"""

	def __init__(self, db: Session = Depends(get_db)):
		"""__init__"""
		self.db = db
		self.user_dal = UserDAL(db)

	def search_users(self, request: SearchUserRequest) -> Pagination[User]:
		try:
			result = self.user_dal.search_users(request.model_dump())
			return result
		except Exception as ex:
			raise ex

	def get_user_by_id(self, user_id: int) -> User:
		"""
		Retrieve a user by their ID

		Args:
		    user_id: The ID of the user to retrieve

		Returns:
		    The user model if found, otherwise None
		"""
		try:
			return self.user_dal.get_user_by_id(user_id)
		except Exception as ex:
			raise ex

	def update_user(self, user_id: int, data: dict) -> User:
		"""
		Update a user's information

		Args:
		    user_id: The ID of the user to update
		    data: A dictionary containing the fields to update

		Returns:
		    The updated user model
		"""
		try:
			user = self.user_dal.get_user_by_id(user_id)
			if not user:
				raise CustomHTTPException(message=_('user_not_found'))

			# Hash the password if it is being updated
			if 'password' in data:
				data['password'] = PasswordUtils.hash_password(data['password'])
			if 'username' in data:
				existing_user = self.user_dal.get_user_by_username(data['username'])
				if existing_user and existing_user.id != user_id:
					raise CustomHTTPException(
						message=_('username_already_exists'),
					)

			# Update the user fields
			for key, value in data.items():
				setattr(user, key, value)

			self.db.commit()
			return user
		except Exception as ex:
			raise ex

	def update_password(self, user: User, param) -> bool:
		password_utils = PasswordUtils()
		current_password = user.password

		password_utils.validate_password(param['new_password'])
		if not password_utils.verify_password(param['current_password'], current_password):
			raise CustomHTTPException(
				message=_('current_password_incorrect'),
			)

		user.password = password_utils.hash_password(param['new_password'])

		self.db.commit()
		return True
