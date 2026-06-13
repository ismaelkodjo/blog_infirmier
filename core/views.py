"""
Vues principales du site (accueil, à propos, parcours, etc.)
"""

from django.shortcuts import render
from django.urls import reverse
from blog.models import Article, Category
from resources.models import Resource
from newsletter.models import NewsletterSubscriber


def home(request):
    """Page d'accueil."""
    featured_articles = Article.objects.filter(status='published', featured=True).select_related('author', 'category')[:3]
    latest_articles = Article.objects.filter(status='published').select_related('author', 'category').order_by('-published_at')[:6]
    popular_articles = Article.objects.filter(status='published').order_by('-views_count')[:4]
    categories = Category.objects.all()[:8]
    recent_resources = Resource.objects.filter(is_public=True).order_by('-created_at')[:4]

    # Stats
    stats = {
        'articles': Article.objects.filter(status='published').count(),
        'categories': Category.objects.count(),
        'subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        'resources': Resource.objects.filter(is_public=True).count(),
    }

    return render(request, 'core/home.html', {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'popular_articles': popular_articles,
        'categories': categories,
        'recent_resources': recent_resources,
        'stats': stats,
        'title': 'Accueil',
    })


def about(request):
    """Page À propos."""
    return render(request, 'core/about.html', {'title': 'À propos'})


def parcours(request):
    """Page Parcours professionnel."""
    return render(request, 'core/parcours.html', {'title': 'Mon Parcours Professionnel'})


def resources_page(request):
    """Page des ressources (vue générale)."""
    from resources.models import Resource
    resources = Resource.objects.filter(is_public=True).order_by('-created_at')[:12]
    return render(request, 'core/resources_page.html', {
        'resources': resources,
        'title': 'Ressources'
    })


def privacy_policy(request):
    """Politique de confidentialité."""
    return render(request, 'core/privacy_policy.html', {'title': 'Politique de confidentialité'})


def legal_notice(request):
    """Mentions légales."""
    return render(request, 'core/legal_notice.html', {'title': 'Mentions légales'})


def error_404(request, exception):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return render(request, 'core/500.html', status=500)
