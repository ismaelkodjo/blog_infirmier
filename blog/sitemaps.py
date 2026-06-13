"""
Sitemaps XML pour le SEO.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Category


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Article.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['core:home', 'core:about', 'core:parcours', 'core:resources_page',
                'blog:article_list', 'contact:contact_view']

    def location(self, item):
        return reverse(item)
