from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Content Security Policy - bardziej restrykcyjne
        if settings.DEBUG:
            # Łagodniejsze CSP dla developmentu
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
            # Bardzo restrykcyjne CSP dla produkcji
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

        # Permissions Policy - rozszerzone
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

        # Podstawowe nagłówki bezpieczeństwa
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Tylko w produkcji
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response["X-XSS-Protection"] = "1; mode=block"

        return response