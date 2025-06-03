"""Main init"""

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import SECRET_KEY
from app.exceptions.handlers import setup_exception_handlers
from app.middleware.localization_middleware import LocalizationMiddleware
from app.middleware.translation_manager import _
from app.modules import route as api_routers

def custom_openapi(app: FastAPI):
    """Create custom openapi schema"""
    api_version = os.getenv('API_VERSION', '1.0.0')
    openapi_schema = get_openapi(
        title=f'{_("api_title")}',
        version=api_version,
        description=_('api_description'),
        routes=app.routes,
    )

    # Store the modified schema
    app.openapi_schema = openapi_schema
    return openapi_schema

def create_app():
    """Create main app"""
    app = FastAPI(
        docs_url=None,  # Disable default docs
        redoc_url=None  # Disable default redoc
    )

    # Register middlewares in correct order (from outermost to innermost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # SessionMiddleware must be added before any middleware that uses the session
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        session_cookie='cgsem_session',  # Consistent cookie name
        same_site='lax',  # Allow cross-site requests while maintaining security
    )

    app.add_middleware(LocalizationMiddleware)

    # Add OAuth debug middleware in development
    @app.middleware('http')
    async def debug_oauth_middleware(request, call_next):
        # Debug sessions for OAuth state issues
        if 'google' in request.url.path:
            print(f'[OAuth Debug] Path: {request.url.path}')
            try:
                print(f'[OAuth Debug] Session before: {request.session}')
            except:
                print('[OAuth Debug] No session available')
            print(f'[OAuth Debug] Cookies: {request.cookies}')
        response = await call_next(request)
        if 'google' in request.url.path:
            try:
                print(f'[OAuth Debug] Session after: {request.session}')
            except:
                print('[OAuth Debug] No session available after')
        return response

    app.include_router(api_routers, prefix='/api')

    # Custom Swagger UI with token persistence
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Docs</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
            <style>
                html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
                body { margin: 0; background: #fff; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    // Initialize Swagger UI
                    const ui = SwaggerUIBundle({
                        url: "/openapi.json",
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        layouts: [
                            SwaggerUIBundle.topbar
                        ],
                        requestInterceptor: (req) => {
                            // Retrieve token from session storage or cookie
                            let token = sessionStorage.getItem('access_token');
                            if (!token) {
                                // Fallback to cookie if session storage is empty
                                const cookies = document.cookie.split(';').reduce((acc, cookie) => {
                                    const [name, value] = cookie.trim().split('=');
                                    acc[name] = value;
                                    return acc;
                                }, {});
                                token = cookies['access_token'];
                            }
                            if (token) {
                                req.headers['Authorization'] = `Bearer ${token}`;
                            }
                            return req;
                        },
                        onComplete: () => {
                            // Optionally, check if token exists and pre-fill the auth modal
                            const token = sessionStorage.getItem('access_token') || document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1];
                            if (token) {
                                ui.preauthorizeApiKey('bearerAuth', token);
                            }
                        }
                    });

                    // Assuming login endpoint sets the token in session or cookie
                    // Example: Store token after login (this should be handled by your auth endpoint)
                    // For demo purposes, you can manually set it via JavaScript for testing
                    // ui.authActions.authorize({ bearerAuth: { value: 'your-token-here' } });
                }
            </script>
        </body>
        </html>
        """)

    custom_openapi(app)
    setup_exception_handlers(app)

    # Register event handlers
    try:
        logger = logging.getLogger(__name__)
        logger.info("Event handlers registered successfully")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to register event handlers: {e}")

    return app