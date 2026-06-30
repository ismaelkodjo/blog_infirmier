from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import Article, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    search_fields = ['name']


class ArticleAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour valider seo_title."""

    class Meta:
        model = Article
        fields = '__all__'

    def clean_seo_title(self):
        value = self.cleaned_data.get('seo_title')
        if value and len(value) > 60:
            raise ValidationError(
                f"Le titre SEO ne doit pas dépasser 60 caractères (actuellement {len(value)})."
            )
        return value


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm

    list_display = [
        'title', 'seo_title_preview', 'author', 'category',
        'status', 'published_at', 'views_count', 'featured'
    ]
    list_filter = ['status', 'category', 'featured', 'created_at']
    search_fields = ['title', 'seo_title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'featured']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author']
    readonly_fields = ['views_count', 'reading_time', 'created_at', 'updated_at', 'seo_title_chars']

    # Organise les champs par sections dans le formulaire d'édition
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'slug', 'summary', 'content', 'cover_image')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_title_chars', 'meta_description', 'meta_keywords'),
            'description': 'Optimisation pour les moteurs de recherche.',
        }),
        ('Classification', {
            'fields': ('author', 'category', 'tags', 'status', 'featured', 'allow_comments')
        }),
        ('Dates', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Statistiques', {
            'fields': ('views_count', 'reading_time'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Titre SEO (aperçu)')
    def seo_title_preview(self, obj):
        """Affiche le titre SEO effectif dans la liste."""
        return obj.get_seo_title()

    @admin.display(description='Caractères titre SEO')
    def seo_title_chars(self, obj):
        """Affiche le nombre de caractères du seo_title dans le formulaire."""
        if obj.seo_title:
            count = len(obj.seo_title)
            color = 'green' if count <= 60 else 'red'
            return f'{count}/60 caractères'
        return f'Non renseigné — le titre principal sera tronqué à 60 caractères.'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['get_author_name', 'article', 'is_approved', 'is_flagged', 'created_at']
    list_filter = ['is_approved', 'is_flagged', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['content', 'author_name', 'author__username']
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
    reject_comments.short_description = "Rejeter les commentaires sélectionnés"