from django.conf import settings

def analytics(request):
    """
    Injecte l'ID Google Analytics dans tous les templates.
    N'est actif qu'en production (DEBUG = False).
    """
    return {
        'GA_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', '') if not settings.DEBUG else ''
    }


def cart_count(request):
    from boutique.cart import Cart
    return {"cart_count": len(Cart(request))}