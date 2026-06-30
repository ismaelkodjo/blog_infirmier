"""
Modèles principaux du blog : Category, Tag, Article, Comment.
"""

import re
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class Category(models.Model):
    """Catégorie d'articles."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, default='bi-folder', verbose_name="Icône Bootstrap")
    color = models.CharField(max_length=20, blank=True, default='#1a6fc4', verbose_name="Couleur")
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name="Meta description SEO")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def get_article_count(self):
        return self.articles.filter(status='published').count()


class Article(models.Model):
    """Article du blog."""

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]

    # Informations principales
    title = models.CharField(max_length=250, verbose_name="Titre")
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name="Titre SEO",
        help_text="Titre affiché dans Google (max 60 caractères). Si vide, le titre principal est utilisé tronqué."
    )
    subtitle = models.CharField(max_length=300, blank=True, null=True, verbose_name="Sous-titre")
    slug = models.SlugField(max_length=270, unique=True, blank=True, verbose_name="Slug")
    summary = models.TextField(max_length=500, verbose_name="Résumé")
    content = RichTextUploadingField(config_name='djiba', verbose_name="Contenu")
    cover_image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Image de couverture")

    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name="Auteur")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="Catégorie")
    tags = TaggableManager(verbose_name="Tags")

    # Statut et dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de publication")

    # SEO
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name="Meta description SEO")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mots-clés SEO")

    # Statistiques
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    reading_time = models.PositiveIntegerField(default=0, verbose_name="Temps de lecture (min)")

    # Options
    featured = models.BooleanField(default=False, verbose_name="Article mis en avant")
    allow_comments = models.BooleanField(default=True, verbose_name="Autoriser les commentaires")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Auto set published date
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Estimate reading time (200 words/min) — strip HTML tags first
        if self.content:
            plain_text = re.sub(r'<[^>]+>', ' ', self.content)
            word_count = len(plain_text.split())
            self.reading_time = max(1, word_count // 200)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})

    def get_seo_title(self):
        """Retourne le titre SEO ≤ 60 caractères, sans couper un mot."""
        source = self.seo_title if self.seo_title else self.title
        if len(source) <= 60:
            return source
        # Tronque sur le dernier espace avant 57 chars et ajoute '...'
        return source[:57].rsplit(' ', 1)[0] + '...'

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)

    def get_comments(self):
        return self.comments.filter(is_approved=True, parent=None).order_by('created_at')

    def get_similar_articles(self):
        """Retourner des articles similaires basés sur la catégorie et les tags."""
        article_tags = self.tags.values_list('id', flat=True)
        similar = list(
            Article.objects.filter(
                status='published',
                category=self.category
            ).exclude(pk=self.pk).distinct()[:4]
        )
        if len(similar) < 4:
            tag_similar = Article.objects.filter(
                status='published',
                tags__in=article_tags
            ).exclude(pk=self.pk).exclude(pk__in=[a.pk for a in similar]).distinct()[:4 - len(similar)]
            similar = similar + list(tag_similar)
        return similar


class Comment(models.Model):
    """Commentaire sur un article."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="Article")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="Réponse à")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name="Auteur")
    author_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom de l'auteur (visiteur)")
    author_email = models.EmailField(blank=True, null=True, verbose_name="Email (visiteur)")
    content = models.TextField(verbose_name="Contenu")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    is_flagged = models.BooleanField(default=False, verbose_name="Signalé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['created_at']

    def __str__(self):
        name = self.author.username if self.author else self.author_name
        return f"Commentaire de {name} sur '{self.article.title}'"

    def get_author_name(self):
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.author_name or "Anonyme"

    def get_replies(self):
        return self.replies.filter(is_approved=True).order_by('created_at')