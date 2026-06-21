"""
Vues du blog : liste, détail, catégories, recherche.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .models import Article, Category, Comment
from .forms import CommentForm, ArticleForm


def article_list(request):
    """Liste de tous les articles publiés."""
    articles = Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    # Recherche
    query = request.GET.get('q', '')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Filtrage par tag
    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)

    # Pagination
    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        articles_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        articles_page = paginator.page(1)

    categories = Category.objects.all()
    popular_articles = Article.objects.filter(status='published').order_by('-views_count')[:5]

    return render(request, 'blog/article_list.html', {
        'articles': articles_page,
        'categories': categories,
        'popular_articles': popular_articles,
        'query': query,
        'tag_slug': tag_slug,
        'title': 'Blog',
    })


@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def article_detail(request, slug):
    """Détail d'un article."""
    article = get_object_or_404(Article, slug=slug, status='published')

    # Incrémenter le compteur de vues (une fois par session)
    session_key = f'viewed_article_{article.pk}'
    if not request.session.get(session_key, False):
        article.increment_views()
        request.session[session_key] = True

    # Commentaires approuvés (racines seulement)
    comments = article.comments.filter(is_approved=True, parent=None).prefetch_related('replies')

    # Formulaire commentaire
    comment_form = CommentForm()

    if request.method == 'POST' and article.allow_comments:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(pk=parent_id)
                except Comment.DoesNotExist:
                    pass
            if request.user.is_authenticated:
                comment.author = request.user
            comment.save()
            messages.success(request, "Votre commentaire a été soumis et est en attente de modération.")
            return redirect('blog:article_detail', slug=slug)

    similar_articles = article.get_similar_articles()

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'similar_articles': similar_articles,
        'title': article.title,
    })


def category_detail(request, slug):
    """Articles d'une catégorie."""
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(status='published', category=category).select_related('author')

    paginator = Paginator(articles, settings.ARTICLES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        articles_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        articles_page = paginator.page(1)

    return render(request, 'blog/category_detail.html', {
        'category': category,
        'articles': articles_page,
        'title': f"Catégorie : {category.name}",
    })


def category_list(request):
    """Liste de toutes les catégories."""
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {
        'categories': categories,
        'title': 'Catégories',
    })


def search_view(request):
    """Vue de recherche."""
    query = request.GET.get('q', '')
    articles = []
    if query:
        articles = Article.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query)
        ).distinct()[:20]
    return render(request, 'blog/search_results.html', {
        'articles': articles,
        'query': query,
        'title': f'Résultats pour "{query}"',
    })


@login_required
def article_create(request):
    """Créer un article (auteurs uniquement)."""
    if not hasattr(request.user, 'profile') or not request.user.profile.is_author():
        messages.error(request, "Vous n'avez pas la permission de créer des articles.")
        return redirect('blog:article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            messages.success(request, "Article créé avec succès.")
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, 'blog/article_form.html', {
        'form': form,
        'title': 'Créer un article',
        'action': 'create',
    })


@login_required
def article_edit(request, slug):
    """Modifier un article."""
    article = get_object_or_404(Article, slug=slug)

    if article.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cet article.")
        return redirect('blog:article_detail', slug=slug)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article modifié avec succès.")
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'blog/article_form.html', {
        'form': form,
        'article': article,
        'title': 'Modifier l\'article',
        'action': 'edit',
    })


@login_required
def article_delete(request, slug):
    """Supprimer un article."""
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cet article.")
        return redirect('blog:article_detail', slug=slug)

    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article supprimé avec succès.")
        return redirect('blog:article_list')

    return render(request, 'blog/article_confirm_delete.html', {
        'article': article,
        'title': 'Supprimer l\'article',
    })


@login_required
@require_POST
def flag_comment(request, comment_id):
    """Signaler un commentaire (authentification requise)."""
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_flagged = True
    comment.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Commentaire signalé.'})
    messages.info(request, "Commentaire signalé à la modération.")
    return redirect('blog:article_detail', slug=comment.article.slug)
