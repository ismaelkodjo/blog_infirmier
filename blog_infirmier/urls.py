"""
URLs principales du projet blog_infirmier.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from ckeditor_uploader import views as ck_views
from blog.sitemaps import ArticleSitemap, CategorySitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    # Admin
    path('djiba/', admin.site.urls),

    # CKEditor — upload et browse réservés aux utilisateurs connectés
    path('ckeditor/upload/', login_required(ck_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', login_required(ck_views.browse), name='ckeditor_browse'),

    # Applications
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('ressources/', include('resources.urls')),
    path('contact/', include('contact.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('tableau-de-bord/', include('dashboard.urls')),
    path('boutique/', include('boutique.urls')),
    path('formations/', include('formations.urls')),

    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
