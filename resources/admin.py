from django.contrib import admin
from .models import Resource
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'category', 'author', 'download_count', 'created_at', 'is_public']
    list_filter = ['file_type', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_public']
