from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if this is an admin request
        is_admin_request = request.path.startswith('/admin/')

        # Content Security Policy
        if settings.DEBUG:
            # Development CSP - more permissive
            if is_admin_request:
                # Very permissive CSP for admin in development
                response["Content-Security-Policy"] = (
                    "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net http://localhost:* http://127.0.0.1:*; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com http://localhost:* http://127.0.0.1:*; "
                    "font-src 'self' https://fonts.gstatic.com data:; "
                    "img-src 'self' data: https: http://localhost:* http://127.0.0.1:*; "
                    "connect-src 'self' https://api.pandascore.co http://localhost:* http://127.0.0.1:* ws://localhost:* wss://localhost:*; "
                    "frame-src 'self'; "
                    "frame-ancestors 'self'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                )
            else:
                # Normal CSP for API/frontend in development
                response["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net http://localhost:* http://127.0.0.1:*; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com http://localhost:* http://127.0.0.1:*; "
                    "font-src 'self' https://fonts.gstatic.com data:; "
                    "img-src 'self' data: https: http://localhost:* http://127.0.0.1:*; "
                    "connect-src 'self' https://api.pandascore.co http://localhost:* http://127.0.0.1:* ws://localhost:* wss://localhost:*; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                )
        else:
            # Production CSP
            if is_admin_request:
                # Admin-specific CSP for production - allows necessary admin functionality
                response["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com data:; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' https://api.pandascore.co; "
                    "frame-src 'self'; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                    "frame-ancestors 'self'; "  # Allow admin frames
                    "upgrade-insecure-requests; "
                )
            else:
                # Restrictive CSP for API/frontend in production
                response["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' https://cdn.jsdelivr.net; "
                    "style-src 'self' https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' https://api.pandascore.co; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                    "frame-ancestors 'none'; "
                    "upgrade-insecure-requests; "
                )

        # Permissions Policy - less restrictive for admin
        if is_admin_request:
            # More permissive for admin interface
            response["Permissions-Policy"] = (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=(), "
            )
        else:
            # Full restrictive permissions for API/frontend
            response["Permissions-Policy"] = (
                "accelerometer=(), "
                "ambient-light-sensor=(), "
                "autoplay=(), "
                "battery=(), "
                "camera=(), "
                "cross-origin-isolated=(), "
                "display-capture=(), "
                "document-domain=(), "
                "encrypted-media=(), "
                "execution-while-not-rendered=(), "
                "execution-while-out-of-viewport=(), "
                "fullscreen=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "keyboard-map=(), "
                "magnetometer=(), "
                "microphone=(), "
                "midi=(), "
                "navigation-override=(), "
                "payment=(), "
                "picture-in-picture=(), "
                "publickey-credentials-get=(), "
                "screen-wake-lock=(), "
                "sync-xhr=(), "
                "usb=(), "
                "web-share=(), "
                "xr-spatial-tracking=()"
            )

        # Basic security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # X-Frame-Options - different for admin vs API
        if is_admin_request:
            response["X-Frame-Options"] = "SAMEORIGIN"  # Allow admin frames
        else:
            response["X-Frame-Options"] = "DENY"  # Deny frames for API

        # Production-only headers
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response["X-XSS-Protection"] = "1; mode=block"

        return response