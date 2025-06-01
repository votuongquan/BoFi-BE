from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from datetime import datetime

from pytz import timezone

from app.core.config import SECRET_KEY, TOKEN_AUDIENCE, TOKEN_ISSUER, ALGORITHM
from app.exceptions.exception import CustomHTTPException, UnauthorizedException
from app.middleware.translation_manager import _
from app.utils.generate_jwt import GenerateJWToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_current_user(data: str = Depends(oauth2_scheme)):
	"""
	Trích xuất thông tin người dùng từ JWT token.
	"""
	try:
		jwt_generator = GenerateJWToken()
		payload = jwt_generator.decode_token(data, SECRET_KEY, TOKEN_ISSUER, TOKEN_AUDIENCE)
		return payload
	except Exception as e:
		print(f'Unexpected error in get_current_user: {e}')
		raise UnauthorizedException(_('token_verification_failed')) from e


def verify_websocket_token(token: str) -> dict:
	"""
	Verify JWT token for WebSocket connections using the same JWT generator
	Returns user info if valid, raises exception if invalid
	"""
	try:
		print(f'\033[94m[verify_websocket_token] Verifying token: {token[:20]}...\033[0m')

		# Use the same JWT generator as the rest of the application
		jwt_generator = GenerateJWToken()
		payload = jwt_generator.decode_token(token, SECRET_KEY, TOKEN_ISSUER, TOKEN_AUDIENCE)

		user_id: str = payload.get('user_id')
		email: str = payload.get('email')
		role: str = payload.get('role')

		print(f'\033[94m[verify_websocket_token] Token payload - user_id: {user_id}, email: {email}, role: {role}\033[0m')

		if user_id is None or email is None:
			print(f'\033[91m[verify_websocket_token] ERROR: Invalid token payload - missing user_id or email\033[0m')
			raise CustomHTTPException(
				message='Invalid token payload',
			)

		print(f'\033[92m[verify_websocket_token] Token verification successful\033[0m')
		return {'user_id': user_id, 'email': email, 'role': role}

	except UnauthorizedException as e:
		print(f'\033[91m[verify_websocket_token] ERROR: Unauthorized - {e}\033[0m')
		raise CustomHTTPException(
			message='Could not validate credentials',
		)
	except Exception as e:
		print(f'\033[91m[verify_websocket_token] ERROR: Token verification failed - {e}\033[0m')
		raise CustomHTTPException(
			message='Token verification failed',
		)


def create_websocket_token(user_data: dict, expires_delta_minutes: int = 60) -> str:
	"""
	Create a JWT token for WebSocket authentication

	Args:
	    user_data: Dictionary containing user information (user_id, email, role)
	    expires_delta_minutes: Token expiration time in minutes (default: 60 minutes)

	Returns:
	    JWT token string
	"""
	try:
		print(f'\033[94m[create_websocket_token] Creating WebSocket token for user: {user_data.get("user_id")}\033[0m')

		# Use the same JWT generator as the rest of the application
		jwt_generator = GenerateJWToken()

		# Create token using the correct method signature from GenerateJWToken
		token = jwt_generator.create_token(
			auth_claims=user_data,
			secret_key=SECRET_KEY,
			issuer=TOKEN_ISSUER,
			audience=TOKEN_AUDIENCE,
			token_validity_in_minutes=expires_delta_minutes,
			current_time=datetime.now(timezone('Asia/Ho_Chi_Minh')),
		)

		print(f'\033[92m[create_websocket_token] WebSocket token created successfully\033[0m')
		return token

	except Exception as e:
		print(f'\033[91m[create_websocket_token] ERROR: Failed to create WebSocket token - {e}\033[0m')
		raise CustomHTTPException(
			message='Failed to create WebSocket token',
		)
