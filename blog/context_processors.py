"""
Context processors pour injecter des données globales dans tous les templates.
"""

from .models import Category, Article
from django.conf import settings


def global_context(request):
    """Données disponibles dans tous les templates."""
    return {
        'global_categories': Category.objects.all()[:10],
        'global_recent_articles': Article.objects.filter(status='published').order_by('-published_at')[:5],
        'site_name': getattr(settings, 'SITE_NAME', 'Blog Infirmier'),
        'site_description': getattr(settings, 'SITE_DESCRIPTION', ''),
        'site_author': getattr(settings, 'SITE_AUTHOR', ''),
    }
