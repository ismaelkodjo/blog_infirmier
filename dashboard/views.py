"""
Tableau de bord administrateur.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from blog.models import Article, Category, Comment
from accounts.models import Profile
from newsletter.models import NewsletterSubscriber
from contact.models import ContactMessage
from resources.models import Resource


@staff_member_required
def dashboard_home(request):
    """Vue principale du tableau de bord."""
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    # Stats globales
    stats = {
        'total_articles': Article.objects.filter(status='published').count(),
        'total_views': Article.objects.aggregate(total=Sum('views_count'))['total'] or 0,
        'total_comments': Comment.objects.filter(is_approved=True).count(),
        'pending_comments': Comment.objects.filter(is_approved=False, is_flagged=False).count(),
        'total_resources': Resource.objects.count(),
        'total_downloads': Resource.objects.aggregate(total=Sum('download_count'))['total'] or 0,
        'total_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        'total_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_authors': Profile.objects.filter(role__in=['author', 'admin']).count(),
    }

    # Articles récents
    recent_articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:10]

    # Commentaires en attente
    pending_comments = Comment.objects.filter(is_approved=False, is_flagged=False).select_related('article')[:10]

    # Articles les plus vus
    popular_articles = Article.objects.filter(status='published').order_by('-views_count')[:5]

    # Articles par mois (12 derniers mois) — pour Chart.js
    articles_by_month = (
        Article.objects
        .filter(created_at__gte=now - timedelta(days=365))
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    chart_labels = [item['month'].strftime('%b %Y') for item in articles_by_month]
    chart_data = [item['count'] for item in articles_by_month]

    # Articles par catégorie — pour Chart.js
    articles_by_cat = (
        Category.objects
        .annotate(count=Count('articles'))
        .values('name', 'count')
        .order_by('-count')[:8]
    )
    cat_labels = [item['name'] for item in articles_by_cat]
    cat_data = [item['count'] for item in articles_by_cat]

    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_articles': recent_articles,
        'pending_comments': pending_comments,
        'popular_articles': popular_articles,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'title': 'Tableau de bord',
    })


@staff_member_required
def moderate_comments(request):
    """Modération des commentaires."""
    from blog.models import Comment
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        try:
            comment = Comment.objects.get(pk=comment_id)
            if action == 'approve':
                comment.is_approved = True
                comment.is_flagged = False
                comment.save()
            elif action == 'delete':
                comment.delete()
        except Comment.DoesNotExist:
            pass
        from django.contrib import messages
        messages.success(request, "Action effectuée.")

    comments = Comment.objects.filter(is_approved=False).select_related('article').order_by('-created_at')
    flagged = Comment.objects.filter(is_flagged=True).select_related('article').order_by('-created_at')

    return render(request, 'dashboard/moderate_comments.html', {
        'comments': comments,
        'flagged': flagged,
        'title': 'Modération des commentaires',
    })
