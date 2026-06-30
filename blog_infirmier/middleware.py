"""
Middleware de sécurité — ajoute les headers manquants :
  - Content-Security-Policy
  - Permissions-Policy
"""


class SecurityHeadersMiddleware:
    """Injecte les headers de sécurité sur chaque réponse HTTP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # ── Content-Security-Policy ──────────────────────────────────────
        # Ressources autorisées par directive :
        #   script-src  : CDN (Bootstrap, Chart.js), Google Tag Manager
        #   style-src   : CDN (Bootstrap Icons), Google Fonts
        #   font-src    : Google Fonts (gstatic), CDN (Bootstrap Icons)
        #   img-src     : self + data URI + tout domaine (images articles)
        #   connect-src : Google Analytics
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "cdn.jsdelivr.net "
            "www.googletagmanager.com "
            "www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline' "
            "cdn.jsdelivr.net "
            "fonts.googleapis.com; "
            "font-src 'self' "
            "fonts.gstatic.com "
            "cdn.jsdelivr.net; "
            "img-src 'self' data: blob: *; "
            "connect-src 'self' "
            "www.google-analytics.com "
            "region1.google-analytics.com; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response["Content-Security-Policy"] = csp

        # ── Permissions-Policy ───────────────────────────────────────────
        # Désactive les API navigateur non utilisées par le site
        permissions = (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=(), "
            "fullscreen=(self)"
        )
        response["Permissions-Policy"] = permissions

        return response
