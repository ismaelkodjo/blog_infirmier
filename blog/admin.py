from django.contrib import admin
from .models import Article, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'views_count', 'featured']
    list_filter = ['status', 'category', 'featured', 'created_at']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'featured']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author']
    readonly_fields = ['views_count', 'reading_time', 'created_at', 'updated_at']


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
